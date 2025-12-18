# Research: AIによるクイズ選択肢の自動生成

**Author:** Gemini
**Status:** Completed
**Created:** 2025-11-10
**Last Updated:** 2025-11-10
**Plan:** [AIによるクイズ選択肢の自動生成](./plan.md)

## 1. Amazon Bedrock APIのリージョンとエンドポイント

- **Decision:** 東京リージョン (`ap-northeast-1`) を使用する。
- **Rationale:** Boto3のドキュメントに基づき、クライアント作成時に `region_name='ap-northeast-1'` を指定します。これにより、レイテンシが最適化され、エンドポイントURLはSDKによって自動的に解決されます。
- **Alternatives considered:** 他のリージョンも選択可能ですが、日本からの利用においては東京リージョンが最も適切です。

## 2. Bedrock API呼び出しのタイムアウトとリトライ設定

- **Decision:** `botocore.config.Config` を利用して、以下の通り設定する。
  - `connect_timeout`: 10秒
  - `read_timeout`: 30秒
  - `retries`:
    - `max_attempts`: 3回
    - `mode`: `standard`
- **Rationale:** ドキュメントで推奨されている `Config` オブジェクトを使用することで、クライアントごとに詳細な設定が可能です。ユーザー体験を考慮し、接続タイムアウトは短めに、AIの応答時間を考慮して読み取りタイムアウトは長めに設定します。リトライは`standard`モードを利用し、一時的なエラーからの回復を図ります。
- **Alternatives considered:**
  - グローバル設定ファイル (`~/.aws/config`) での設定も可能ですが、アプリケーションの挙動をコード内で完結させるため `Config` オブジェクトを選択します。
  - `adaptive` リトライモードは実験的な機能であるため、安定性を重視し `standard` を選択します。

## 3. Bedrock APIのエラーハンドリング

- **Decision:** `botocore.exceptions.ClientError` を `try...except` ブロックで捕捉する。例外オブジェクト内の `error.response['Error']['Code']` を確認し、エラーの種類に応じた処理を行う。
- **Rationale:** Boto3の公式ドキュメントで推奨されているエラーハンドリング方法です。これにより、`AccessDeniedException` や `ThrottlingException` といったサービス固有のエラーを正確に識別し、ログレベルの調整やフォールバック処理への移行を確実に行うことができます。
- **Alternatives considered:**
  - `client.exceptions.ServiceException` のように、サービス固有の例外クラスを直接捕捉する方法もありますが、`ClientError` を捕捉する方がより汎用的であり、未知のエラーにも対応しやすいため、こちらを選択します。
