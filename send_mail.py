import os
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# =====================
# 環境変数
# =====================
MAIL_FROM = os.environ["MAIL_FROM"]
MAIL_TO = os.environ["MAIL_TO"]
GMAIL_APP_PASSWORD = os.environ["GMAIL_APP_PASSWORD"]
INBOX_JSON_URL = os.environ["INBOX_JSON_URL"]

MAIL_HOST = "smtp.gmail.com"
MAIL_PORT = 587

# =====================
# Inbox JSON取得
# =====================
response = requests.get(INBOX_JSON_URL, timeout=10)
response.raise_for_status()
data = response.json()

items = data.get("items", [])

# =====================
# メール本文生成
# =====================
lines = []

for i, item in enumerate(items, start=1):
    lines.append(
        f"{i}. {item['title']}\n"
        f"   作成日: {item['created']}\n"
        f"   Do      : {item['actions']['do']}\n"
        f"   Waiting : {item['actions']['waiting']}\n"
        f"   Someday : {item['actions']['someday']}\n"
        f"   Done    : {item['actions']['done']}\n"
        f"   Drop    : {item['actions']['drop']}\n"
    )

body = "\n".join(lines) if lines else "Inboxは空です。"

# =====================
# メール作成
# =====================
msg = MIMEMultipart()
msg["From"] = MAIL_FROM
msg["To"] = MAIL_TO
msg["Subject"] = f"Inbox Triage ({len(items)} items)"

msg.attach(MIMEText(body, "plain", "utf-8"))

# =====================
# Gmail SMTP送信
# =====================
with smtplib.SMTP(MAIL_HOST, MAIL_PORT) as server:
    server.starttls()
    server.login(MAIL_FROM, GMAIL_APP_PASSWORD)
    server.send_message(msg)

print("✅ Mail sent successfully")
