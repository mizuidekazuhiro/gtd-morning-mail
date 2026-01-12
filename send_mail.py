import requests
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# =====================
# 設定（ここだけ調整）
# =====================
INBOX_API_URL = "https://notion-inbox-triage.kazuhiro-mizuide.workers.dev/api/inbox"

GMAIL_ADDRESS = os.environ.get("GMAIL_ADDRESS")      # 例: xxxx@gmail.com
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASS")  # 16桁のアプリPW
MAIL_TO = os.environ.get("MAIL_TO", )

# =====================
# Inbox JSON 取得
# =====================
def fetch_inbox():
    res = requests.get(INBOX_API_URL, timeout=10)
    res.raise_for_status()
    return res.json()

# =====================
# HTMLメール生成
# =====================
def build_html(items):
    rows = []

    for item in items:
        title = item["title"]
        created = item["created"] or ""
        actions = item["actions"]

        buttons = " ".join(
            f'<a href="{url}" style="margin-right:8px;">{label}</a>'
            for label, url in actions.items()
        )

        rows.append(f"""
        <tr>
          <td style="padding:8px;border-bottom:1px solid #ddd;">
            <b>{title}</b><br>
            <small>{created}</small><br>
            {buttons}
          </td>
        </tr>
        """)

    if not rows:
        rows.append("<tr><td>🎉 Inbox は空です</td></tr>")

    return f"""
    <html>
    <body style="font-family:-apple-system,BlinkMacSystemFont,sans-serif;">
      <h2>📥 Inbox Triage</h2>
      <table style="width:100%;border-collapse:collapse;">
        {''.join(rows)}
      </table>
    </body>
    </html>
    """

# =====================
# メール送信
# =====================
def send_mail(subject, html_body):
    msg = MIMEMultipart("alternative")
    msg["From"] = GMAIL_ADDRESS
    msg["To"] = MAIL_TO
    msg["Subject"] = subject

    msg.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
        server.send_message(msg)

# =====================
# main
# =====================
def main():
    data = fetch_inbox()

    items = data["items"]
    count = data["count"]

    subject = f"Inbox｜{count} 件｜{datetime.now().strftime('%Y-%m-%d')}"
    html = build_html(items)

    send_mail(subject, html)
    print("✅ Mail sent successfully")

if __name__ == "__main__":
    main()
