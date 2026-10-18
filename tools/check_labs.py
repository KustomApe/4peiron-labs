"""ラボが docs/rules.md の決まりを守っているかを確かめる。CI と手元の両方で使う。

    python3 tools/check_labs.py            # 全ラボ
    python3 tools/check_labs.py red/xxx    # 1 台だけ

compose の書き方の揺れ（短い書き方・長い書き方）に左右されないよう、
`docker compose config --format json` で正規化したものを見る。Docker が要る。

決まりを破っていれば終了コード 1。証拠に実在しそうな IP アドレスやドメインが
あるときは警告だけ出す（証拠の中のバージョン番号などを拾うことがあるため）。
"""
import gzip
import ipaddress
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TRACKS = ("foundation", "red", "blue", "purple")

# 受講者の PC の中に閉じない設定。どれも、あれば違反
FORBIDDEN_KEYS = ("ports", "privileged", "cap_add", "devices", "extra_hosts", "dns")
HOST_NAMESPACES = ("pid", "ipc", "uts", "userns_mode", "cgroup")

# 証拠に出てきてよい IP アドレス。文書用・プライベート・ループバックなど
ALLOWED_NETS = [ipaddress.ip_network(n) for n in (
    "192.0.2.0/24", "198.51.100.0/24", "203.0.113.0/24",   # 文書用（RFC 5737）
    "10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16",       # プライベート
    "127.0.0.0/8", "0.0.0.0/32", "169.254.0.0/16", "100.64.0.0/10",
    "224.0.0.0/4", "255.255.255.255/32",
)]
# 直前が「/」のもの（「Chrome/128.0.0.0」のような版）は除く
IPV4 = re.compile(r"(?<![\d./])(\d{1,3}(?:\.\d{1,3}){3})(?![\d.])")
# 例示用でないドメイン。拾いすぎないよう、よくある TLD だけを見る
DOMAIN = re.compile(r"\b((?:[a-z0-9-]+\.)+(?:com|net|org|jp|io|co|info|biz|ru|cn|xyz|top))\b", re.I)
ALLOWED_DOMAIN = re.compile(r"(^|\.)example\.(com|net|org|jp|(co|ne|or|ac|go)\.jp)$|\.(example|test|invalid|localhost)$", re.I)


def lab_dirs(args: list[str]) -> list[Path]:
    if args:
        return [ROOT / a for a in args]
    return sorted(p.parent for t in TRACKS for p in (ROOT / t).glob("*/compose.yaml"))


def compose_config(lab: Path) -> dict:
    out = subprocess.run(
        ["docker", "compose", "-f", str(lab / "compose.yaml"), "config", "--format", "json"],
        capture_output=True, text=True,
    )
    if out.returncode != 0:
        raise ValueError(out.stderr.strip())
    return json.loads(out.stdout)


def check_compose(lab: Path, config: dict) -> list[str]:
    problems = []
    networks = config.get("networks") or {}
    for name, svc in config.get("services", {}).items():
        where = f"{name}:"
        for key in FORBIDDEN_KEYS:
            if svc.get(key):
                problems.append(f"{where} {key} は使わない")
        for key in HOST_NAMESPACES:
            if svc.get(key) == "host":
                problems.append(f"{where} {key}: host は使わない")
        if not svc.get("read_only"):
            problems.append(f"{where} read_only: true が無い")
        if "ALL" not in (svc.get("cap_drop") or []):
            problems.append(f"{where} cap_drop: [ALL] が無い")
        if "no-new-privileges:true" not in (svc.get("security_opt") or []):
            problems.append(f"{where} security_opt: [no-new-privileges:true] が無い")

        # ネットワーク: つながないか、外への経路が無い（internal）ネットワークだけにつなぐ
        mode = svc.get("network_mode")
        if mode is not None and mode != "none":
            problems.append(f"{where} network_mode: {mode} は使わない（none か、internal のネットワークにする）")
        if mode is None:
            for net in svc.get("networks") or {}:
                if not (networks.get(net) or {}).get("internal"):
                    problems.append(f"{where} ネットワーク {net} に internal: true が無い")

        # ホストからつなぐのは、ラボのディレクトリの中だけ・読み取り専用
        for vol in svc.get("volumes") or []:
            if vol.get("type") != "bind":
                continue
            source = Path(vol["source"]).resolve()
            if not source.is_relative_to(lab.resolve()):
                problems.append(f"{where} ラボの外（{source}）をつないでいる")
            if not vol.get("read_only"):
                problems.append(f"{where} {vol['target']} が読み取り専用（:ro）でない")
    for name, net in networks.items():
        if net.get("external"):
            problems.append(f"ネットワーク {name}: external は使わない")
    return problems


def is_target_lab(config: dict) -> bool:
    """調査用のコンテナのほかに、ネットワークにつながるサービスがあるラボ。"""
    return any(s.get("network_mode") != "none" for s in config.get("services", {}).values())


def check_target_lab(lab: Path, config: dict) -> list[str]:
    """標的を置くラボだけにかかる決まり（docs/rules.md の「標的を置くラボ」）。"""
    problems = []
    for name, svc in config.get("services", {}).items():
        where = f"{name}:"
        # 中身の分からない外のイメージをそのまま動かさない。土台は Dockerfile の FROM で使う
        context = (svc.get("build") or {}).get("context")
        if not context:
            problems.append(f"{where} build が無い（このリポジトリの Dockerfile からビルドする）")
        elif not Path(context).resolve().is_relative_to(ROOT):
            problems.append(f"{where} build の場所がリポジトリの外（{context}）")
        # 再起動の設定があると、PC を立ち上げ直したときに標的が勝手に動き出す
        if svc.get("restart") not in (None, "no"):
            problems.append(f"{where} restart: {svc['restart']} は使わない")
    readme = lab / "README.md"
    text = readme.read_text() if readme.is_file() else ""
    if not re.search(r"^## 標的について", text, re.M):
        problems.append("README.md に「## 標的について」の節が無い")
    if not re.search(r"^### About the target", text, re.M):
        problems.append("README.md に「### About the target」の節が無い")
    return problems


def check_files(lab: Path, config: dict) -> list[str]:
    problems = []
    readme = lab / "README.md"
    if not readme.is_file():
        return ["README.md が無い"]
    text = readme.read_text()
    if not re.search(r"[ぁ-んァ-ン]", text):
        problems.append("README.md に日本語が無い")
    if not re.search(r"^## English", text, re.M):
        problems.append("README.md に「## English」の節が無い")
    if not is_target_lab(config) and not (lab / "evidence").is_dir():
        problems.append("evidence/ が無い")
    return problems


def read_text(path: Path) -> str:
    raw = path.read_bytes()
    if path.suffix == ".gz":
        raw = gzip.decompress(raw)
    return raw.decode("utf-8", errors="ignore")


def scan_evidence(lab: Path) -> list[str]:
    warnings = []
    for path in sorted(p for p in lab.rglob("*") if p.is_file() and p.name != "compose.yaml"):
        text = read_text(path)
        rel = path.relative_to(lab)
        ips = set()
        for m in IPV4.findall(text):
            try:
                ip = ipaddress.ip_address(m)
            except ValueError:
                continue
            if not any(ip in n for n in ALLOWED_NETS):
                ips.add(m)
        if ips:
            warnings.append(f"{rel}: 文書用でない IP アドレス {', '.join(sorted(ips)[:5])}")
        domains = {d.lower() for d in DOMAIN.findall(text) if not ALLOWED_DOMAIN.search(d)}
        if domains:
            warnings.append(f"{rel}: example 系でないドメイン {', '.join(sorted(domains)[:5])}")
    return warnings


def main(args: list[str]) -> int:
    failed = False
    for lab in lab_dirs(args):
        name = lab.relative_to(ROOT)
        try:
            config = compose_config(lab)
        except ValueError as e:
            print(f"NG    {name}: docker compose config が通らない — {e}")
            failed = True
            continue
        problems = check_compose(lab, config) + check_files(lab, config)
        if is_target_lab(config):
            problems += check_target_lab(lab, config)
        for p in problems:
            print(f"NG    {name}: {p}")
        for w in scan_evidence(lab):
            print(f"warn  {name}: {w}")
        if not problems:
            print(f"ok    {name}")
        failed |= bool(problems)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
