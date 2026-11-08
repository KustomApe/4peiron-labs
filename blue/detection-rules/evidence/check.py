"""書いたルールを、単体テストとバックテストで確かめる。

    python3 /evidence/check.py ~/rules.py          # 4 本とも
    python3 /evidence/check.py ~/rules.py D2       # 1 本だけ
    python3 /evidence/check.py ~/rules.py --en     # English output

ルールごとに、次の 2 つがどちらも通ったときだけフラグを出します。

1. 単体テスト   tests/d1.json などの表。入力のイベントと、鳴るべきキーの組
2. バックテスト events.jsonl（2 週間分）に当てて、鳴るべきものを全部拾い、
                 拾ってはいけないものを 1 つも拾わないこと

バックテストの正解は、キーのハッシュだけを持っています。見逃し・誤検知がある
ときは、そのキー（送信元の IP アドレスかイベントの ID）を最大 5 件まで出します。
"""
import hashlib
import importlib.util
import json
import sys
import traceback
from pathlib import Path

EV = Path(__file__).resolve().parent
LAB = "blue-detection-rules"

RULES = {
    "D1": ("d1_ssh_burst", "src_ip"),
    "D2": ("d2_sudoers_change", "id"),
    "D3": ("d3_web_probe", "client_ip"),
    "D4": ("d4_remote_sudo", "id"),
}

# バックテストで鳴るべきキーの sha256("<ルール>:<キー>")
EXPECTED = {
    "D1": [
        "1c7db4141c277f3e4a554558a0c6b6a45cd66d6ea5b5cb70c12e92718934dcca",
        "5fb1cb71f015c95d8d7b6901d2485e749424922e96aac62a44f86104e110b00a",
        "89d95f0104938126ce98968278591203457326e650070310465a896835242abc",
    ],
    "D2": [
        "19638ea008835c32940552afeff56387c414531161baafb696d05e85c7d3e055",
        "54554960fb6599fb544f154c23bf31aecd9d855318faf9d708c087ac3fc4ec2f",
        "7a154e18c61b8f13caf6169b9c8278bf9f3bf1f783c79e851314853435bf2921",
        "e3198855b6b07155c6ee9f127716430b4fbb782658f9ca5711b94f1971fbcd24",
    ],
    "D3": [
        "18c4e8fc4717ba999baf7a5c6d4a921f7b791e8eae8b4d7097d48c5a789668c9",
        "2a7b0b91c170610f82e20a3fd5d13eccc005bbe78f5a090d97933dadd0e52112",
        "d51c2e3d98235bab8a1d320185032ed042069a53ec6b8aa19bcc90d72b246c36",
    ],
    "D4": [
        "7c00a1f7f9d5d87d77bf39b4926c1fda625ef0d522c1d2e04194d7261924a909",
        "9610691493896eda92c2092be00af6d279554bf8ad76cf21a2c8d1679366daf7",
        "af9ff386dfe0a086357c77c4ff5806a35f83f07ebead78d9ca21b79c8fe0f901",
    ],
}

EN = "--en" in sys.argv
MSG = {
    "usage": ("使い方: python3 /evidence/check.py ~/rules.py [D1 D2 D3 D4]",
              "usage: python3 /evidence/check.py ~/rules.py [D1 D2 D3 D4]"),
    "missing": ("関数 {} がありません", "function {} is missing"),
    "crashed": ("ルールが例外で止まりました", "the rule raised an exception"),
    "not_iter": ("ルールはキーの集合（set や list）を返してください。返ったのは {}",
                 "a rule must return a collection of keys (set, list); got {}"),
    "unit": ("単体テスト", "unit tests"),
    "back": ("バックテスト", "backtest"),
    "miss": ("見逃し", "missed"),
    "fp": ("誤検知", "false positives"),
    "pass": ("合格", "pass"),
    "fail": ("まだ", "not yet"),
    "expected_got": ("鳴るべき {} / 返したもの {}", "expected {} / returned {}"),
    "flag": ("フラグ", "flag"),
}


def say(key, *args):
    return MSG[key][1 if EN else 0].format(*args)


def sha(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def flag(rule: str, keys) -> str:
    return "4P{" + rule.lower() + "-" + sha(f"{LAB}|{rule}|" + ",".join(sorted(keys)))[:12] + "}"


def load_rules(path: Path):
    spec = importlib.util.spec_from_file_location("rules", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run(func, events):
    """ルールを走らせて、キーの集合を返す。だめなら (None, 理由)。"""
    try:
        got = func([dict(e) for e in events])  # ルールが中身を書き換えても次に響かないよう写しを渡す
    except Exception:
        return None, say("crashed") + "\n" + "".join(traceback.format_exc(limit=-3))
    if got is None or isinstance(got, (str, bytes, dict)) or not hasattr(got, "__iter__"):
        return None, say("not_iter", type(got).__name__)
    return {str(k) for k in got}, ""


def show(keys, limit=5):
    keys = sorted(keys)
    more = f" …(+{len(keys) - limit})" if len(keys) > limit else ""
    return ", ".join(keys[:limit]) + more


def check(rule, module, events) -> bool:
    name, field = RULES[rule]
    print(f"\n== {rule}  {name}")
    func = getattr(module, name, None)
    if func is None:
        print("  " + say("missing", name))
        return False

    ok = True
    cases = json.loads((EV / "tests" / f"{rule.lower()}.json").read_text())
    passed = 0
    for case in cases:
        got, why = run(func, case["events"])
        title = case["name_en"] if EN else case["name"]
        if got is None:
            print(f"  FAIL  {title}: {why}")
        elif got != set(case["expect"]):
            print(f"  FAIL  {title}: " + say("expected_got", sorted(case["expect"]), sorted(got)))
        else:
            passed += 1
            continue
        ok = False
    print(f"  {say('unit')}: {passed}/{len(cases)}")

    got, why = run(func, events)
    if got is None:
        print(f"  {say('back')}: {why}")
        return False
    want = set(EXPECTED[rule])
    universe = {str(e[field]) for e in events if field in e}
    missed = {k for k in universe if sha(f"{rule}:{k}") in want and k not in got}
    found = {k for k in got if sha(f"{rule}:{k}") in want}
    false_pos = got - found
    print(f"  {say('back')}: {len(found)}/{len(want)}  {say('miss')} {len(want) - len(found)}  {say('fp')} {len(false_pos)}")
    if missed:
        print(f"    {say('miss')}: {show(missed)}")
    if false_pos:
        print(f"    {say('fp')}: {show(false_pos)}")
    if ok and len(found) == len(want) and not false_pos:
        print(f"  {say('pass')}  {say('flag')}: {flag(rule, found)}")
        return True
    print(f"  {say('fail')}")
    return False


def main(argv):
    args = [a for a in argv if a != "--en"]
    if not args:
        print(say("usage"))
        return 2
    module = load_rules(Path(args[0]).expanduser())
    targets = [a.upper() for a in args[1:]] or list(RULES)
    events = [json.loads(line) for line in (EV / "events.jsonl").read_text().splitlines() if line.strip()]
    results = [check(rule, module, events) for rule in targets if rule in RULES]
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
