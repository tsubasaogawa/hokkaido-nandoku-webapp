# Quickstart: AIによるクイズ選択肢の自動生成

**Branch**: `002-bedrock-quiz-options`
**Spec**: [spec.md](./spec.md)
**Plan**: [plan.md](./plan.md)

## 1. 概要

この機能は、クイズの不正解の選択肢をAmazon Bedrock APIを利用して動的に生成します。

## 2. 環境構築

### 2.1. AWS認証情報の設定

アプリケーションはAWS Lambda上での実行を想定しており、IAMロールによってBedrockへのアクセス権限が付与されます。

ローカルで開発・テストを行う場合は、以下の環境変数を設定してください。

```bash
export AWS_ACCESS_KEY_ID="YOUR_ACCESS_KEY"
export AWS_SECRET_ACCESS_KEY="YOUR_SECRET_KEY"
export AWS_SESSION_TOKEN="YOUR_SESSION_TOKEN" # (Optional)
export AWS_DEFAULT_REGION="ap-northeast-1"
```

### 2.2. Python依存関係のインストール

プロジェクトルートで以下のコマンドを実行し、必要なライブラリをインストールします。

```bash
pip install -r requirements.txt
```

`boto3` が `requirements.txt` に含まれていることを確認してください。含まれていない場合は追加してください。

## 3. アプリケーションの実行

以下のコマンドでFastAPIサーバーを起動します。

```bash
uvicorn src.main:app --reload
```

サーバーは `http://127.0.0.1:8000` で起動します。

## 4. 動作確認

Webブラウザで `http://127.0.0.1:8000` にアクセスし、クイズページを開きます。
問題が表示された際に、正解と紛らわしい選択肢が3つ表示されていれば成功です。

Bedrock APIとの連携でエラーが発生した場合は、コンソールログを確認し、フォールバックとしてダミーの選択肢が表示されることを確認してください。
