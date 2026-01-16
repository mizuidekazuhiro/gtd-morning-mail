import os
import json
import requests
import smtplib
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
# HTML メール生成
# =====================
def build_html_mail(data):
    items = data.get("items", [])

    rows = ""
    for item in items:
        title = item["title"]
        created = item["created"] or ""
        actions = item.get("actions",{})
        def btn(label, url, color):
            return f"""
            <a href="{url}" style="
              padding:6px 10px;
              margin-right:4px;
              background:{color};
              color:white;
              text-decoration:none;
              border-radius:4px;
              font-size:12px;
              display:inline-block;
            ">{label}</a>
            """

        def safe_btn(label, key, color):
            url = actions.get(key)
            if not url:
                return ""
            return btn(label, url, color)

        rows += f"""
        <tr>
          <td style="padding:8px;border-bottom:1px solid #ddd;">
            <b>{title}</b><br>
            <span style="color:#888;font-size:12px;">{created}</span>
          </td>
        <td style="padding:8px;border-bottom:1px solid #ddd;">
          {safe_btn("Do", "Do", "#2563eb")}
          {safe_btn("Waiting", "Waiting", "#9333ea")}
          {safe_btn("Someday", "Someday", "#16a34a")}
          {safe_btn("Done", "Done", "#6b7280")}
          {safe_btn("Drop", "Drop", "#dc2626")}
        </td>
        </tr>
        """

    html = f"""
    <html>
    <body style="font-family:Arial, sans-serif;background:#f9fafb;padding:16px;">
      <h2>📥 Inbox Triage ({len(items)} items)</h2>

      <table width="100%" cellpadding="0" cellspacing="0"
        style="background:white;border-radius:8px;">
        {rows}
      </table>

      <p style="margin-top:24px;color:#666;font-size:12px;">
        ※ ボタンを押すと確認画面が開きます
      </p>
    </body>
    </html>
    """
    return html


# =====================
# Gmail 送信
# =====================
def send_mail(subject, html):
    msg = MIMEMultipart("alternative")
    msg["From"] = MAIL_FROM
    msg["To"] = ", ".join(MAIL_TO)   # 表示用
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
    html = build_html_mail(data)
    subject = f"Inbox｜{data.get('count', 0)} 件"
    send_mail(subject, html)


if __name__ == "__main__":
    main()
