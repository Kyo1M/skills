#!/usr/bin/env python3
"""docx を Google ドキュメントに変換して Google Drive のフォルダに置き、ページ分けなしにする。

使い方:
    python3 docx_to_gdocs.py check --folder <フォルダID> (--account <email> | --token-cmd "<コマンド>")
        フォルダの名前・ファイルを作れるか・共有の相手（ドメインと権限ごとの数）を出す
    python3 docx_to_gdocs.py upload <docx> --folder <フォルダID> (--account <email> | --token-cmd "<コマンド>")
                             [--name <文書名>] [--replace <ドキュメントID>] [--pages]
        docx を Google ドキュメントにする。--replace は既存の文書の中身を差し替える（URL と共有はそのまま）

- 画像は docx の中に入っているので、変換で文書の中に取り込まれる。画像をリンクで公開しない
- 同じ名前の文書がフォルダにあり --replace が無いときは、作らずに止める（二重にしない）
- 上げた後に、見出し・表・画像の数を docx と照らす（pandoc が要る）。合わなければ終了コード 1
- 認証: --account は gog（Google Workspace CLI）に登録したアカウントのリフレッシュトークンから、
  その場でアクセストークンを作る（gog の既定の OAuth クライアントを使う）。
  --token-cmd はアクセストークンを標準出力に出す任意のコマンド（例: gcloud auth print-access-token）。シェルを通さずに実行する
- 標準ライブラリだけで動く
"""

import argparse
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

GDOC = "application/vnd.google-apps.document"
DOCX = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
DRIVE = "https://www.googleapis.com/drive/v3/files"
UPLOAD = "https://www.googleapis.com/upload/drive/v3/files"
DOCS = "https://docs.googleapis.com/v1/documents"
GOG_CREDENTIALS = [
    Path.home() / "Library/Application Support/gogcli/credentials.json",   # macOS
    Path.home() / ".config/gogcli/credentials.json",                       # Linux
]

sys.path.insert(0, str(Path(__file__).resolve().parent))
from md_to_docx import count_structure  # noqa: E402


# ---------------------------------------------------------------- 認証

def token_from_gog(account: str) -> str:
    creds_path = next((p for p in GOG_CREDENTIALS if p.exists()), None)
    if creds_path is None:
        raise SystemExit("gog の OAuth クライアント（credentials.json）が見つかりません。--token-cmd を使ってください")
    with tempfile.TemporaryDirectory() as work:
        exported = Path(work) / "token.json"
        result = subprocess.run(["gog", "auth", "tokens", "export", account, "--out", str(exported), "--overwrite"],
                                capture_output=True, text=True)
        if result.returncode != 0:
            raise SystemExit(f"gog にアカウントがありません: {account}\n"
                             f"（gog auth add {account} --services drive,docs で登録する）\n{result.stderr.strip()}")
        refresh = json.loads(exported.read_text())["refresh_token"]
    creds = json.loads(creds_path.read_text())
    creds = creds.get("installed") or creds.get("web") or creds
    body = urllib.parse.urlencode({"client_id": creds["client_id"], "client_secret": creds["client_secret"],
                                   "refresh_token": refresh, "grant_type": "refresh_token"}).encode()
    try:
        with urllib.request.urlopen("https://oauth2.googleapis.com/token", body, timeout=60) as response:
            return json.load(response)["access_token"]
    except urllib.error.HTTPError as error:
        reason = json.loads(error.read().decode() or "{}").get("error", error.code)
        raise SystemExit(f"アクセストークンを作れませんでした（{reason}）。"
                         f"gog auth add {account} --services drive,docs で登録し直す")


def token_from_command(command: str) -> str:
    result = subprocess.run(shlex.split(command), capture_output=True, text=True)
    if result.returncode != 0 or not result.stdout.strip():
        raise SystemExit(f"--token-cmd が失敗しました: {result.stderr.strip()}")
    return result.stdout.strip().splitlines()[-1]


# ---------------------------------------------------------------- API

class ApiError(Exception):
    def __init__(self, code: int, message: str):
        super().__init__(message)
        self.code = code


class Api:
    def __init__(self, token: str):
        self.token = token

    def call(self, url, body=None, method=None, headers=None, raw=None):
        h = {"Authorization": f"Bearer {self.token}", **(headers or {})}
        data = raw
        if body is not None:
            h["Content-Type"] = "application/json; charset=UTF-8"
            data = json.dumps(body).encode()
        request = urllib.request.Request(url, data=data, headers=h, method=method)
        try:
            with urllib.request.urlopen(request, timeout=600) as response:
                text = response.read().decode()
                return (json.loads(text) if text else {}), response.headers
        except urllib.error.HTTPError as error:
            detail = error.read().decode()[:400]
            raise ApiError(error.code, f"{method or 'GET'} {url.split('?')[0]} → {error.code}\n{detail}")

    def get(self, url, **params):
        params.setdefault("supportsAllDrives", "true")
        return self.call(f"{url}?{urllib.parse.urlencode(params)}")[0]

    def upload(self, path: Path, metadata: dict, file_id: str | None = None) -> str:
        """resumable で上げる。file_id があれば中身を差し替える（Google ドキュメントは docx から変換し直される）"""
        params = urllib.parse.urlencode({"uploadType": "resumable", "supportsAllDrives": "true"})
        url = f"{UPLOAD}/{file_id}?{params}" if file_id else f"{UPLOAD}?{params}"
        _, headers = self.call(url, body=metadata, method="PATCH" if file_id else "POST",
                               headers={"X-Upload-Content-Type": DOCX})
        data = path.read_bytes()
        result, _ = self.call(headers["Location"], method="PUT", raw=data,
                              headers={"Content-Type": DOCX, "Content-Length": str(len(data))})
        return result["id"]


def sharing_summary(api: Api, file_id: str):
    """共有の相手を、ドメインと権限ごとの数にまとめる（個人のアドレスは出さない）。取れなければ None"""
    permissions, page = [], None
    try:
        while True:
            params = {"fields": "nextPageToken,permissions(type,role,emailAddress,domain)", "pageSize": "100"}
            if page:
                params["pageToken"] = page
            result = api.get(f"{DRIVE}/{file_id}/permissions", **params)
            permissions += result.get("permissions", [])
            page = result.get("nextPageToken")
            if not page:
                break
    except ApiError:
        return None
    summary = {}
    for p in permissions:
        if p["type"] == "anyone":
            who = "リンクを知っている全員"
        elif p["type"] == "domain":
            who = f"ドメイン全体: {p.get('domain')}"
        else:
            who = (p.get("emailAddress") or "?").split("@")[-1]
        summary[(who, p["role"])] = summary.get((who, p["role"]), 0) + 1
    return summary


def doc_counts(api: Api, doc_id: str) -> tuple[dict, str]:
    doc = api.call(f"{DOCS}/{doc_id}")[0]
    counts = {"見出し": 0, "表": 0, "画像": len(doc.get("inlineObjects", {}))}
    for element in doc["body"]["content"]:
        style = element.get("paragraph", {}).get("paragraphStyle", {}).get("namedStyleType", "")
        if style.startswith("HEADING") or style == "TITLE":
            counts["見出し"] += 1
        if "table" in element:
            counts["表"] += 1
    mode = doc.get("documentStyle", {}).get("documentFormat", {}).get("documentMode", "PAGES")
    return counts, mode


def docx_counts(path: Path) -> dict:
    markdown = subprocess.run(["pandoc", str(path), "-t", "gfm"], check=True, capture_output=True, text=True).stdout
    counts = count_structure(markdown)
    counts["画像"] = len(re.findall(r"<img |!\[", markdown))
    return counts


def with_retry(action, already_done=None, attempts=3):
    """Google 側の一時的なエラー（5xx・429）なら待ってやり直す。やり直す前に、できていないかを確かめる"""
    for attempt in range(1, attempts + 1):
        try:
            return action()
        except ApiError as error:
            if error.code < 500 and error.code != 429 or attempt == attempts:
                raise
            print(f"一時的なエラー（{error.code}）。{5 * attempt} 秒後にやり直します", file=sys.stderr)
            time.sleep(5 * attempt)
            done = already_done() if already_done else None
            if done:
                return done


# ---------------------------------------------------------------- コマンド

def check(api: Api, folder: str) -> int:
    info = api.get(f"{DRIVE}/{folder}", fields="id,name,mimeType,capabilities/canAddChildren")
    print(f"フォルダ: {info['name']}")
    print(f"ファイルを作れるか: {'はい' if info.get('capabilities', {}).get('canAddChildren') else 'いいえ'}")
    print_sharing("共有の相手", sharing_summary(api, folder))
    return 0


def print_sharing(label: str, summary) -> None:
    if summary is None:
        print(f"{label}: 取得できませんでした（権限が足りない）")
        return
    print(f"{label}:")
    for (who, role), n in sorted(summary.items()):
        print(f"  - {who}（{role}）: {n}")
    if any(who == "リンクを知っている全員" for who, _ in summary):
        print(f"注意: 「リンクを知っている全員」に共有されています（{label}）", file=sys.stderr)


def upload(api: Api, args) -> int:
    path = Path(args.docx).expanduser().resolve()
    if not path.exists():
        print(f"docx がありません: {path}", file=sys.stderr)
        return 2
    name = args.name or path.stem
    folder = api.get(f"{DRIVE}/{args.folder}", fields="name,capabilities/canAddChildren")
    if not folder.get("capabilities", {}).get("canAddChildren"):
        print(f"フォルダにファイルを作れません: {folder.get('name')}", file=sys.stderr)
        return 2
    folder_sharing = sharing_summary(api, args.folder)
    if folder_sharing and any(who == "リンクを知っている全員" for who, _ in folder_sharing):
        print("注意: フォルダが「リンクを知っている全員」に共有されています", file=sys.stderr)

    if args.replace:
        target = api.get(f"{DRIVE}/{args.replace}", fields="id,name,mimeType,parents")
        if target["mimeType"] != GDOC:
            print(f"Google ドキュメントではありません: {target['name']}", file=sys.stderr)
            return 2
        if args.folder not in target.get("parents", []):
            print(f"差し替える文書が指定のフォルダにありません: {target['name']}", file=sys.stderr)
            return 2
        print_sharing("差し替える文書の共有の相手", sharing_summary(api, args.replace))
        name = args.name or target["name"]   # 名前は --name が無ければ変えない
        doc_id = with_retry(lambda: api.upload(path, {"name": name} if args.name else {}, file_id=args.replace))
        action = "差し替え"
    else:
        escaped = name.replace("\\", "\\\\").replace("'", "\\'")
        query = f"'{args.folder}' in parents and name = '{escaped}' and trashed = false"
        def find_existing():
            return api.get(DRIVE, q=query, fields="files(id,name)", corpora="allDrives",
                           includeItemsFromAllDrives="true").get("files", [])

        existing = find_existing()
        if existing:
            print(f"同じ名前の文書がフォルダにあります: {name}（{existing[0]['id']}）\n"
                  "差し替えるなら --replace <ドキュメントID> を付ける", file=sys.stderr)
            return 2
        doc_id = with_retry(lambda: api.upload(path, {"name": name, "mimeType": GDOC, "parents": [args.folder]}),
                            already_done=lambda: (find_existing() or [{}])[0].get("id"))
        action = "作成"

    if not args.pages:
        api.call(f"{DOCS}/{doc_id}:batchUpdate", method="POST", body={"requests": [{"updateDocumentStyle": {
            "documentStyle": {"documentFormat": {"documentMode": "PAGELESS"}}, "fields": "documentFormat"}}]})

    expected = docx_counts(path)
    actual, mode = doc_counts(api, doc_id)
    print(f"{action}: {name}")
    print(f"URL: https://docs.google.com/document/d/{doc_id}/edit")
    print(f"ドキュメントID: {doc_id}（作り直すときは --replace {doc_id}）")
    print(f"ページ: {'ページ分けなし' if mode == 'PAGELESS' else 'ページあり'}")
    print("| 項目 | docx | Google ドキュメント |")
    print("|---|---|---|")
    ok = True
    for key in ("見出し", "表", "画像"):
        mark = "" if expected[key] == actual[key] else " ← 不一致"
        ok = ok and not mark
        print(f"| {key} | {expected[key]} | {actual[key]}{mark} |")
    return 0 if ok else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("check", "upload"):
        p = sub.add_parser(name)
        if name == "upload":
            p.add_argument("docx")
            p.add_argument("--name", help="文書名（既定は docx のファイル名）")
            p.add_argument("--replace", help="中身を差し替える既存の Google ドキュメントの ID")
            p.add_argument("--pages", action="store_true", help="ページ分けなしにしない")
        p.add_argument("--folder", required=True)
        auth = p.add_mutually_exclusive_group(required=True)
        auth.add_argument("--account", help="gog に登録したアカウント")
        auth.add_argument("--token-cmd", help="アクセストークンを標準出力に出すコマンド")
    args = parser.parse_args()
    if args.command == "upload" and not shutil.which("pandoc"):
        print("pandoc がありません（brew install pandoc）", file=sys.stderr)
        return 2
    api = Api(token_from_command(args.token_cmd) if args.token_cmd else token_from_gog(args.account))
    try:
        return check(api, args.folder) if args.command == "check" else upload(api, args)
    except ApiError as error:
        print(error, file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
