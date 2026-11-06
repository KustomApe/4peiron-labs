"""直した設定一式を、株式会社サンプルの Linux ベースラインに照らして点検する。

    cp -r /evidence/server ~/server        # 直すのは写しのほう
    python3 /evidence/audit.py ~/server
    python3 /evidence/audit.py ~/server --en

点検は 4 つの分野（K・S・A・W）に分かれていて、分野の中の項目が**すべて**通ったら、
その分野のフラグを出します。項目には 2 種類あります。

    弱いところ  ベースラインに合わない設定が残っていないか
    壊さない    直したせいで、要る機能が止まっていないか（`*` の付いた項目）

台帳（/evidence/inventory/staff.csv）は読むだけです。直すのは ~/server の中だけにします。
"""
import csv
import hashlib
import re
import sys
from pathlib import Path

LAB = "blue-hardening-fix"
EVIDENCE = Path(__file__).resolve().parent
EN = "--en" in sys.argv


def L(ja, en):
    return en if EN else ja


# --------------------------------------------------------------------------
# 読む
# --------------------------------------------------------------------------
def staff():
    with (EVIDENCE / "inventory" / "staff.csv").open(encoding="utf-8") as f:
        return [r for r in csv.DictReader(f)]


def groups(server: Path) -> dict[str, set[str]]:
    """group ファイルの 4 列目（補助メンバー）だけで数える。"""
    out = {}
    for line in (server / "group").read_text().splitlines():
        if line.strip() and not line.startswith("#"):
            name, _, _, members = (line.split(":") + ["", "", ""])[:4]
            out[name] = {m for m in members.split(",") if m}
    return out


def sshd_effective(server: Path) -> dict[str, str]:
    """sshd と同じく、Include をその場で展開し、**最初に**出てきた値を使う。"""
    seen: dict[str, str] = {}

    def read(path: Path):
        for raw in path.read_text().splitlines():
            line = raw.split("#", 1)[0].strip()
            if not line:
                continue
            key, _, value = line.partition(" ")
            key, value = key.lower(), value.strip()
            if key == "match":
                return  # このラボの設定には Match は無い。あれば、そこから先は読まない
            if key == "include":
                for pattern in value.split():
                    rel = pattern.removeprefix("/etc/ssh/")
                    for inc in sorted((server / "ssh").glob(rel)):
                        read(inc)
                continue
            seen.setdefault(key, value)

    read(server / "ssh" / "sshd_config")
    return seen


def sysctl_effective(server: Path) -> dict[str, str]:
    """sysctl.d の *.conf を名前の順に読み、**後から**出てきた値を使う。"""
    out = {}
    for path in sorted((server / "sysctl.d").glob("*.conf")):
        for raw in path.read_text().splitlines():
            line = raw.strip()
            if not line or line[0] in "#;":
                continue
            key, _, value = line.partition("=")
            out[key.strip()] = value.strip()
    return out


def sudoers_files(server: Path) -> list[Path]:
    """sudo と同じく、sudoers.d の中で「.」を含む名前と「~」で終わる名前は読まない。"""
    files = [server / "sudoers"]
    d = server / "sudoers.d"
    if d.is_dir():
        files += sorted(p for p in d.iterdir() if p.is_file() and "." not in p.name and not p.name.endswith("~"))
    return files


def sudo_rules(server: Path):
    """(誰, NOPASSWD か, コマンドの一覧) と、Defaults の一覧。"""
    rules, defaults = [], []
    for path in sudoers_files(server):
        for raw in path.read_text().splitlines():
            line = raw.strip()
            if not line or (line.startswith("#") and not line.startswith("#include")):
                continue
            if line.startswith(("#include", "@include")):
                continue
            if line.startswith("Defaults"):
                defaults += [d.strip() for d in line[len("Defaults"):].split(",")]
                continue
            m = re.match(r"(\S+)\s+\S+\s*=\s*(?:\([^)]*\)\s*)?(.*)$", line)
            if not m:
                continue
            who, rest = m.groups()
            nopasswd = False
            while True:
                tag = re.match(r"(NOPASSWD|PASSWD|NOEXEC|EXEC|SETENV|NOSETENV)\s*:\s*", rest)
                if not tag:
                    break
                nopasswd = nopasswd or tag.group(1) == "NOPASSWD"
                rest = rest[tag.end():]
            commands = [c.strip() for c in rest.split(",") if c.strip()]
            rules.append((who, nopasswd, commands, path.name))
    return rules, defaults


def permissions(server: Path) -> dict[str, tuple[str, str, str]]:
    out = {}
    for raw in (server / "permissions.txt").read_text().splitlines():
        line = raw.strip()
        if line and not line.startswith("#"):
            mode, owner, group, path = line.split(None, 3)
            out[path] = (mode.zfill(4), owner, group)
    return out


# -- nginx ----------------------------------------------------------------
class Block:
    def __init__(self, name, args):
        self.name, self.args, self.items = name, args, []

    def directives(self, name):
        return [i for i in self.items if not isinstance(i, Block) and i[0] == name]

    def blocks(self, name):
        return [i for i in self.items if isinstance(i, Block) and i.name == name]


def nginx_parse(text: str) -> Block:
    text = re.sub(r"#[^\n]*", "", text)
    tokens = re.findall(r'"[^"]*"|\'[^\']*\'|[{};]|[^\s{};]+', text)
    root, stack, words = Block("main", []), [], []
    stack.append(root)
    for tok in tokens:
        if tok == "{":
            block = Block(words[0], words[1:]) if words else Block("", [])
            stack[-1].items.append(block)
            stack.append(block)
            words = []
        elif tok == ";":
            if words:
                stack[-1].items.append((words[0], [w.strip("\"'") for w in words[1:]]))
            words = []
        elif tok == "}":
            stack.pop()
            words = []
        else:
            words.append(tok)
    return root


def nginx(server: Path):
    """nginx.conf の http の中に、sites-enabled のファイルを include の位置で入れたもの。"""
    def expand(block: Block):
        items = []
        for item in block.items:
            if not isinstance(item, Block) and item[0] == "include" and "sites-enabled" in item[1][0]:
                for site in sorted((server / "nginx" / "sites-enabled").glob("*")):
                    items += nginx_parse(site.read_text()).items
            elif isinstance(item, Block):
                expand(item)
                items.append(item)
            else:
                items.append(item)
        block.items = items
    root = nginx_parse((server / "nginx" / "nginx.conf").read_text())
    expand(root)
    http = root.blocks("http")[0]
    return http


def is_tls(server_block: Block) -> bool:
    return any("443" in " ".join(args) for _, args in server_block.directives("listen"))


def effective(name, *levels):
    """内側から見て最初に書かれている階層の値（nginx の継承）。"""
    for level in levels:
        found = level.directives(name)
        if found:
            return found
    return []


# --------------------------------------------------------------------------
# 点検の項目
# --------------------------------------------------------------------------
def check_kernel(server: Path):
    s = sysctl_effective(server)

    def eq(key, want):
        got = s.get(key)
        return got == want, L(f"{key} = {got}（ベースライン: {want}）", f"{key} = {got} (baseline: {want})")

    yield "K1", *eq("net.ipv4.ip_forward", "0")
    yield "K2", *eq("net.ipv4.conf.all.accept_redirects", "0")
    yield "K3", *eq("net.ipv4.conf.all.send_redirects", "0")
    yield "K4", *eq("net.ipv4.tcp_syncookies", "1")
    kptr = s.get("kernel.kptr_restrict", "0")
    yield "K5", kptr in ("1", "2"), L(f"kernel.kptr_restrict = {kptr}（ベースライン: 1 以上）",
                                      f"kernel.kptr_restrict = {kptr} (baseline: 1 or more)")
    yield "K6", *eq("fs.suid_dumpable", "0")
    conn = s.get("net.core.somaxconn")
    yield "K7*", conn is not None and conn.isdigit() and int(conn) >= 4096, L(
        f"net.core.somaxconn = {conn}（アプリが 4096 以上を要る）",
        f"net.core.somaxconn = {conn} (the app needs 4096 or more)")


def check_ssh(server: Path):
    c = sshd_effective(server)
    g = groups(server)

    def eq(key, want):
        got = c.get(key.lower())
        return got == want, L(f"{key} {got}（ベースライン: {want}）", f"{key} {got} (baseline: {want})")

    yield "S1", *eq("PermitRootLogin", "no")
    yield "S2", *eq("PasswordAuthentication", "no")
    tries = c.get("maxauthtries", "6")
    yield "S3", tries.isdigit() and int(tries) <= 4, L(f"MaxAuthTries {tries}（ベースライン: 4 以下）",
                                                       f"MaxAuthTries {tries} (baseline: 4 or fewer)")
    yield "S4", *eq("X11Forwarding", "no")
    allow = c.get("allowgroups")
    yield "S5", allow == "sshusers", L(f"AllowGroups {allow}（ベースライン: sshusers だけ）",
                                       f"AllowGroups {allow} (baseline: sshusers only)")
    others = [k for k in ("allowusers", "denyusers", "denygroups") if k in c]
    can = set() if allow is None or others else set().union(*(g.get(x, set()) for x in allow.split()))
    if allow is None:
        can = None
    want = {r["user"] for r in staff() if r["status"] == "在籍" and r["ssh"] == "yes"}
    if can is None:
        yield "S6*", False, L("AllowGroups が無いので、だれが入れるかを台帳と比べられない",
                              "no AllowGroups, so who can log in cannot be compared with the staff list")
    elif others:
        yield "S6*", False, L(f"{', '.join(others)} は使わず、sshusers の顔ぶれで決める",
                              f"do not use {', '.join(others)}; decide by the members of sshusers")
    else:
        extra, missing = sorted(can - want), sorted(want - can)
        yield "S6*", not extra and not missing, L(
            f"SSH で入れる人が台帳と違う（入れてはいけない: {extra or 'なし'} / 入れなくなった: {missing or 'なし'}）"
            if extra or missing else "SSH で入れる人が台帳と同じ",
            f"login access differs from the staff list (should not: {extra or 'none'} / locked out: {missing or 'none'})"
            if extra or missing else "login access matches the staff list")


def full_sudo_users(rules, g):
    out = set()
    for who, _nopasswd, commands, _ in rules:
        if "ALL" in commands:
            out |= g.get(who[1:], set()) if who.startswith("%") else {who}
    return out - {"root"}


DEPLOY_RULE = "/usr/bin/systemctl restart members"


def check_accounts(server: Path):
    rules, defaults = sudo_rules(server)
    g = groups(server)
    nopass = [(who, cmds, f) for who, np, cmds, f in rules if np]
    bad = [f"{f}: {who} {', '.join(c for c in cmds if not (who == 'deploy' and c == DEPLOY_RULE))}"
           for who, cmds, f in nopass if not (who == "deploy" and cmds == [DEPLOY_RULE])]
    yield "A1", not bad, L(
        "パスワード無しの sudo が、deploy の再起動のほかにある: " + " / ".join(bad) if bad
        else "パスワード無しの sudo は deploy の再起動だけ",
        "passwordless sudo beyond deploy's restart: " + " / ".join(bad) if bad
        else "passwordless sudo is only deploy's restart")
    have = full_sudo_users(rules, g)
    want = {r["user"] for r in staff() if r["status"] == "在籍" and r["sudo"] == "yes"}
    extra, missing = sorted(have - want), sorted(want - have)
    yield "A2", not extra, L(f"管理者の sudo を持つべきでない人: {extra}" if extra else "管理者の sudo は台帳のとおり",
                             f"should not have full sudo: {extra}" if extra else "full sudo matches the staff list")
    yield "A3*", not missing, L(f"管理者の sudo を失った人: {missing}" if missing else "台帳の管理者は sudo を使える",
                                f"lost full sudo: {missing}" if missing else "the listed admins keep full sudo")
    yield "A4*", any(who == "deploy" and DEPLOY_RULE in cmds for who, _, cmds, _ in rules), L(
        "deploy が systemctl restart members を実行できる" if any(who == "deploy" and DEPLOY_RULE in cmds for who, _, cmds, _ in rules)
        else "deploy が systemctl restart members を実行できなくなった（デプロイが止まる）",
        "deploy can run systemctl restart members" if any(who == "deploy" and DEPLOY_RULE in cmds for who, _, cmds, _ in rules)
        else "deploy can no longer run systemctl restart members (deploys stop)")
    yield "A5", "use_pty" in defaults, L("Defaults use_pty " + ("がある" if "use_pty" in defaults else "が無い"),
                                          "Defaults use_pty is " + ("set" if "use_pty" in defaults else "missing"))

    perms = permissions(server)
    want_perm = {"/etc/shadow": ("0640", "root", "shadow"), "/etc/sudoers": ("0440", "root", "root"),
                 "/etc/ssh/ssh_host_ed25519_key": ("0600", "root", "root"),
                 "/home/deploy/.ssh/authorized_keys": ("0600", "deploy", "deploy")}
    for p in sudoers_files(server)[1:]:
        want_perm[f"/etc/sudoers.d/{p.name}"] = ("0440", "root", "root")
    wrong = [f"{path} {perms.get(path, ('?',) * 3)[0]} {':'.join(perms.get(path, ('?',) * 3)[1:])} → {m} {o}:{gr}"
             for path, (m, o, gr) in want_perm.items() if perms.get(path) != (m, o, gr)]
    yield "A6", not wrong, L("権限が違う: " + " / ".join(wrong) if wrong else "決めたファイルの権限は合っている",
                             "wrong permissions: " + " / ".join(wrong) if wrong else "the listed files have the right permissions")
    open_ = [f"{path} {m}" for path, (m, _, _) in perms.items()
             if int(m[-1]) & 2 and not (int(m[0]) & 1)]  # だれでも書ける。ただし sticky（/tmp）は除く
    yield "A7", not open_, L("だれでも書ける: " + ", ".join(open_) if open_ else "だれでも書ける場所は /tmp だけ",
                             "world-writable: " + ", ".join(open_) if open_ else "only /tmp is world-writable")


def check_web(server: Path):
    http = nginx(server)
    servers = http.blocks("server")
    tls = [s for s in servers if is_tls(s)]
    plain = [s for s in servers if not is_tls(s)]

    tokens = effective("server_tokens", http)
    yield "W1", bool(tokens) and tokens[-1][1] == ["off"], L(
        f"server_tokens {tokens[-1][1][0] if tokens else '（既定は on）'}（ベースライン: off）",
        f"server_tokens {tokens[-1][1][0] if tokens else '(default on)'} (baseline: off)")

    bad = []
    for s in tls:
        got = set(effective("ssl_protocols", s, http)[-1][1]) if effective("ssl_protocols", s, http) else {"TLSv1.2", "TLSv1.3"}
        if not got or got - {"TLSv1.2", "TLSv1.3"}:
            bad.append(" ".join(sorted(got)))
    yield "W2", not bad, L(f"効いている ssl_protocols: {' / '.join(bad)}（ベースライン: TLSv1.2 と TLSv1.3 だけ）" if bad
                           else "ssl_protocols は TLSv1.2 と TLSv1.3 だけ",
                           f"effective ssl_protocols: {' / '.join(bad)} (baseline: TLSv1.2 and TLSv1.3 only)" if bad
                           else "ssl_protocols is TLSv1.2 and TLSv1.3 only")

    on = [" ".join(b.args) for s in servers for b in s.blocks("location") if b.directives("autoindex") and b.directives("autoindex")[-1][1] == ["on"]]
    yield "W3", not on, L(f"autoindex on の場所: {on}" if on else "一覧の表示（autoindex）はどこも off",
                          f"autoindex on at: {on}" if on else "autoindex is off everywhere")

    def hsts_ok(headers):
        for _, args in headers:
            if args and args[0].lower() == "strict-transport-security":
                m = re.search(r"max-age=(\d+)", " ".join(args[1:]))
                return bool(m) and int(m.group(1)) >= 31536000
        return False

    weak = []
    for s in tls:
        places = [("server", s, effective("add_header", s, http))]
        for loc in s.blocks("location"):
            places.append((" ".join(loc.args), loc, effective("add_header", loc, s, http)))
        weak += [name for name, _, headers in places if not hsts_ok(headers)]
    yield "W4", not weak, L(f"HSTS（max-age 31536000 以上）が届かない場所: {weak}" if weak
                            else "どの場所にも HSTS が届く",
                            f"HSTS (max-age 31536000 or more) is not sent at: {weak}" if weak
                            else "HSTS is sent everywhere")

    def hides_dotfiles(s):
        for loc in s.blocks("location"):
            if len(loc.args) == 2 and loc.args[0] in ("~", "~*"):
                try:
                    pattern = re.compile(loc.args[1].strip("\"'"), re.I if loc.args[0] == "~*" else 0)
                except re.error:
                    continue
                blocks_it = loc.directives("deny") and loc.directives("deny")[-1][1] == ["all"] or \
                    any(args and args[0] in ("403", "404") for _, args in loc.directives("return"))
                if blocks_it and all(pattern.search(p) for p in ("/.env", "/.git/config", "/uploads/.htpasswd")) \
                        and not any(pattern.search(p) for p in ("/static/app.js", "/", "/uploads/photo.png")):
                    return True
        return False
    yield "W5", bool(tls) and all(hides_dotfiles(s) for s in tls), L(
        "「.」で始まるファイル（/.env・/.git/ など）を返さない location がある" if tls and all(hides_dotfiles(s) for s in tls)
        else "「.」で始まるファイル（/.env・/.git/ など）を拒む location（正規表現・deny all か return 404）が無い",
        "a location refuses dot files (/.env, /.git/ ...)" if tls and all(hides_dotfiles(s) for s in tls)
        else "no regex location that refuses dot files (/.env, /.git/ ...) with deny all or return 404")

    def serves_app(s):
        names = [a for _, args in s.directives("server_name") for a in args]
        root = [loc for loc in s.blocks("location") if loc.args == ["/"]]
        static = [loc for loc in s.blocks("location") if loc.args == ["/static/"]]
        return ("members.example" in names and root and root[0].directives("proxy_pass")
                and root[0].directives("proxy_pass")[-1][1] == ["http://127.0.0.1:8000"] and static)
    redirect = any(any(args[:1] == ["301"] and args[1:2] == ["https://$host$request_uri"] for _, args in s.directives("return"))
                   for s in plain)
    ok = bool(tls) and all(serves_app(s) for s in tls) and redirect
    yield "W6*", ok, L("443 でアプリ（/ と /static/）を返し、80 は https へ転送している" if ok
                       else "サイトが壊れた: 443 の / → 127.0.0.1:8000・/static/、または 80 → https の転送が無い",
                       "443 serves the app (/ and /static/) and 80 redirects to https" if ok
                       else "the site broke: 443 lacks / → 127.0.0.1:8000 or /static/, or 80 no longer redirects to https")


AREAS = [
    ("K", L("カーネルとネットワーク", "Kernel and network"), check_kernel),
    ("S", L("SSH", "SSH"), check_ssh),
    ("A", L("アカウント・sudo・権限", "Accounts, sudo and permissions"), check_accounts),
    ("W", L("Web サーバーと TLS", "Web server and TLS"), check_web),
]


def flag(area: str, ids) -> str:
    digest = hashlib.sha256(f"{LAB}|{area}|{','.join(sorted(ids))}".encode()).hexdigest()
    return "4P{h" + area.lower() + "-" + digest[:12] + "}"


def audit(server: Path) -> dict[str, str | None]:
    """分野ごとのフラグ（通らなかった分野は None）。出力もここで出す。"""
    out = {}
    for area, title, check in AREAS:
        print(f"\n== {area}  {title}")
        try:
            results = list(check(server))
        except (OSError, ValueError, IndexError, KeyError) as e:
            print(L(f"  読めないファイルがある: {type(e).__name__}: {e}", f"  a file could not be read: {type(e).__name__}: {e}"))
            out[area] = None
            continue
        for cid, ok, why in results:
            print(f"  {'PASS' if ok else 'FAIL'}  {cid:<4} {why}")
        if all(ok for _, ok, _ in results):
            out[area] = flag(area, [cid for cid, _, _ in results])
            print(f"  {L('合格', 'pass')}  {L('フラグ', 'flag')}: {out[area]}")
        else:
            out[area] = None
            print(f"  {L('まだ', 'not yet')}")
    return out


def main(argv):
    args = [a for a in argv if a != "--en"]
    server = Path(args[0]).expanduser() if args else Path.home() / "server"
    if server.resolve() == (EVIDENCE / "server").resolve():
        print(L("/evidence は読み取り専用です。cp -r /evidence/server ~/server で写してから直してください",
                "/evidence is read-only. Copy it first: cp -r /evidence/server ~/server"))
    if not (server / "sshd_config").exists() and not (server / "ssh").is_dir():
        print(L(f"{server} に設定一式がありません", f"no configuration found in {server}"))
        return 2
    flags = audit(server)
    return 0 if all(flags.values()) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
