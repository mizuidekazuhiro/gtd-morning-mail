import os
import requests
import smtplib
from datetime import datetime, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


# =====================
# 環境変数
# =====================
MAIL_FROM = os.environ["MAIL_FROM"]
MAIL_TO = os.environ["MAIL_TO"].split(",")
GMAIL_APP_PASSWORD = os.environ["GMAIL_APP_PASSWORD"]
INBOX_JSON_URL = os.environ["INBOX_JSON_URL"]


# =====================
# Inbox JSON 取得
# =====================
def fetch_inbox():
    res = requests.get(INBOX_JSON_URL, timeout=20)
    res.raise_for_status()
    return res.json()


# =====================
# ユーティリティ
# =====================
def _get_any(item, keys, default=None):
    for k in keys:
        if k in item and item[k] is not None:
            return item[k]
    return default

def _to_int(v):
    try:
        return int(v)
    except Exception:
        return None

def _parse_dt(v):
    """
    期待する入力例:
      - "2026-01-18"
      - "2026-01-18T09:12:34Z"
      - "2026-01-18T09:12:34+09:00"
    """
    if not v:
        return None
    if isinstance(v, datetime):
        return v
    if isinstance(v, str):
        s = v.strip()
        if s.endswith("Z"):
            s = s[:-1] + "+00:00"
        try:
            return datetime.fromisoformat(s)
        except Exception:
            # 日付だけの場合
            try:
                return datetime.fromisoformat(s + "T00:00:00")
            except Exception:
                return None
    return None


# =====================
# Today’s view フィルタ（Status=Do OR Waiting days>=3）
# =====================
def is_todays_view_item(item):
    status = _get_any(item, ["status", "Status", "state", "State"])
    waiting_days = _get_any(item, ["waiting_days", "waitingDays", "Waiting days", "waiting_days_num"])
    wd = _to_int(waiting_days)

    cond1 = (status == "Do")
    cond2 = (wd is not None and wd >= 3)
    return cond1 or cond2


# =====================
# Doになってから◯日（Since Do を使用）
# =====================
def do_days_text(item):
    status = _get_any(item, ["status", "Status", "state", "State"])
    if status != "Do":
        return ""

    # Notionプロパティ Since Do を JSON に載せている前提
    since_do = _get_any(item, ["since_do", "sinceDo", "Since Do", "SinceDo"])
    dt = _parse_dt(since_do)
    if not dt:
        return ""

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    today = datetime.now(timezone.utc).date()
    days = (today - dt.date()).days
    if days < 0:
        days = 0

    return f"Doになってから {days}日"


# =====================
# HTML メール生成（ボタン無し）
# =====================
def build_html_mail(data):
    items = data.get("items", [])
    items = [it for it in items if is_todays_view_item(it)]

    rows = ""
    for item in items:
        title = item.get("title", "(no title)")
        created = item.get("created") or ""

        status = _get_any(item, ["status", "Status", "state", "State"]) or ""
        waiting_days = _get_any(item, ["waiting_days", "waitingDays", "Waiting days", "waiting_days_num"])
        wd = _to_int(waiting_days)

        meta_parts = []
        if status:
            meta_parts.append(f"Status: {status}")

        dd = do_days_text(item)
        if dd:
            meta_parts.append(dd)

        if wd is not None:
            meta_parts.append(f"Waiting days: {wd}")

        meta = " / ".join(meta_parts)

        rows += f"""
        <tr>
          <td style="padding:10px;border-bottom:1px solid #eee;">
            <div style="font-size:14px;line-height:1.4;"><b>{title}</b></div>
            <div style="color:#666;font-size:12px;margin-top:4px;line-height:1.4;">{meta}</div>
            <div style="color:#999;font-size:11px;margin-top:2px;">{created}</div>
          </td>
        </tr>
        """

    html = f"""
    <html>
    <body style="font-family:Arial, sans-serif;background:#f9fafb;padding:16px;">
      <h2>🗓 Today’s view ({len(items)} items)</h2>

      <table width="100%" cellpadding="0" cellspacing="0"
        style="background:white;border-radius:8px;overflow:hidden;">
        {rows}
      </table>

      <p style="margin-top:18px;color:#666;font-size:12px;">
        ※ 操作はショートカットで行う（メール内ボタン無し）
      </p>
    </body>
    </html>
    """
    return html, len(items)


# =====================
# Gmail 送信
# =====================
def send_mail(subject, html):
    msg = MIMEMultipart("alternative")
    msg["From"] = MAIL_FROM
    msg["To"] = ", ".join(MAIL_TO)  # 表示用
    msg["Subject"] = subject

    msg.attach(MIMEText(html, "html", "utf-8"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(MAIL_FROM, GMAIL_APP_PASSWORD)
        server.send_message(msg, to_addrs=MAIL_TO)  # 実送信先


# =====================
# main
# =====================
def main():
    data = fetch_inbox()
    print("TOP KEYS:", list(data.keys()))
    items = data.get("items", [])
    print("ITEMS COUNT:", len(items))
    if items:
        print("FIRST ITEM KEYS:", list(items[0].keys()))
        print("FIRST ITEM SAMPLE:", items[0])
    # ここで return してメール送らない
    return