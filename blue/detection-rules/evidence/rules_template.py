"""検知ルールのひな形。ホームに写してから書き換えます。

    cp /evidence/rules_template.py ~/rules.py
    vi ~/rules.py
    python3 /evidence/check.py ~/rules.py

どの関数も、イベント（dict）のリストを受け取り、鳴らす「キー」の集合を返します。
キーがルールごとに違うことに気をつけてください（README の「ルールの仕様」）。

    D1  送信元の IP アドレス（src_ip）
    D2  イベントの ID（id）
    D3  送信元の IP アドレス（client_ip）
    D4  sudo のイベントの ID（id）

時刻は "2026-10-21T15:02:00Z" の形の文字列です。下の at() で datetime に直せます。
標準ライブラリだけで書けます（ipaddress・datetime・json など）。
"""
import ipaddress
import json
from datetime import datetime, timedelta
from pathlib import Path

EVIDENCE = Path("/evidence")


def at(text):
    """"2026-10-21T15:02:00Z" を datetime（UTC）に直す。"""
    return datetime.fromisoformat(text.replace("Z", "+00:00"))


def exceptions_for(rule):
    """exceptions.json のうち、そのルールのものだけ。"""
    rows = json.loads((EVIDENCE / "exceptions.json").read_text())
    return [x for x in rows if x["rule"] == rule]


def probe_paths():
    """probe_paths.txt の 1 行 1 つのパス（# の行と空行は除く）。"""
    lines = (EVIDENCE / "probe_paths.txt").read_text().splitlines()
    return [line.strip() for line in lines if line.strip() and not line.startswith("#")]


def d1_ssh_burst(events):
    """同じ送信元からの SSH ログイン失敗の急増。鳴らす送信元の IP アドレスを返す。"""
    found = set()
    return found


def d2_sudoers_change(events):
    """sudoers の変更。鳴らすイベントの ID を返す。"""
    found = set()
    return found


def d3_web_probe(events):
    """Web の探り（よく狙われるパスを、短い間に何種類も）。鳴らす送信元の IP アドレスを返す。"""
    found = set()
    return found


def d4_remote_sudo(events):
    """外から SSH で入ってすぐの sudo。鳴らす sudo のイベントの ID を返す。"""
    found = set()
    return found
