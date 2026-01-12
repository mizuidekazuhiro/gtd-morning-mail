# GTD Morning Mail

GitHub Actions から Cloudflare Worker の JSON を取得し、
Inbox タスクを Gmail に毎朝送信する最小構成です。

## Files
- send_mail.py : Worker JSON → HTMLメール → Gmail送信
- .github/workflows/morning_mail.yml : cron実行

## Required Secrets
- GMAIL_ADDRESS
- GMAIL_APP_PASSWORD
- MAIL_TO
- WORKER_URL
