# gtd-morning-mail

## 目的 / 概要

Inbox JSON を取得し、条件に合う項目を HTML メールとして送信するためのスクリプトです。

## 必須環境変数

- `MAIL_FROM`: 送信元メールアドレス
- `MAIL_TO`: 送信先メールアドレス（カンマ区切り）
- `GMAIL_APP_PASSWORD`: Gmail のアプリパスワード
- `INBOX_JSON_URL`: Inbox JSON の取得先 URL

## 実行手順

1. 必須環境変数を設定する。
2. 以下を実行する。

```bash
python send_mail.py
```

## 入力 JSON の期待形式

トップレベルに `items` 配列があり、各要素は以下のようなキーを持つことを想定しています。

- `title`: タイトル
- `status`: ステータス（例: `Do`）
- `waiting_days`: Waiting days（日数）
- `since_do`: Since Do（日付または日時）
- `created`: 作成日時

※ 実装上は `status` の別名（`Status`, `state`, `State`）や、`waiting_days` の別名
（`waitingDays`, `Waiting days`, `waiting_days_num`）、`since_do` の別名（`sinceDo`, `Since Do`, `SinceDo`）
にも対応しています。

## フィルタ条件

「Today’s view」向けに、以下の条件のいずれかを満たすアイテムのみをメールに含めます。

- `status` が `Do`
- `waiting_days` が 3 以上

## Since Do の日数計算

- `status` が `Do` の場合のみ `since_do` を参照します。
- `since_do` は `YYYY-MM-DD` または ISO8601 形式（例: `2026-01-18T09:12:34Z`）を想定しています。
- 日数は「UTC の今日の日付」から `since_do` の日付を引いた差分で計算します。
- 未来日付の場合は 0 日として扱います。

## 注意事項

現状の `main()` はデバッグ用に `return` しており、メール送信を行いません。送信を有効にする場合は `return` を削除してください。
