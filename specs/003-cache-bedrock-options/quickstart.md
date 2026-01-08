# Quickstart: DynamoDB Caching for Bedrock Options

このドキュメントでは、`003-cache-bedrock-options` 機能の実装とテストに関するクイックスタートガイドを提供します。

## 概要

この機能は、既存の `hokkaido-nandoku-webapp` の `main.py` にあるLambdaハンドラに、DynamoDBへのキャッシングロジックを追加することで実装されます。Bedrock APIを呼び出す前に、まずDynamoDBキャッシュを確認し、キャッシュがあればそれを返し、なければBedrock APIを呼び出して結果をキャッシュに保存します。

## 開発環境のセットアップ

### 1. DynamoDBテーブルの作成

この機能には、キャッシュを保存するためのDynamoDBテーブルが必要です。Terraformを使用してインフラを管理します。

1.  **Terraform定義の更新 (`terraform/main.tf`)**:
    新しいDynamoDBテーブルリソースを追加します。パーティションキーは `cache_key` (String) とし、TTLを `expires_at` 属性で有効にします。

    ```terraform
    resource "aws_dynamodb_table" "quiz_cache" {
      name         = "hokkaido-nandoku-quiz-cache"
      billing_mode = "PAY_PER_REQUEST"
      hash_key     = "cache_key"

      attribute {
        name = "cache_key"
        type = "S"
      }

      ttl {
        attribute_name = "expires_at"
        enabled        = true
      }

      tags = {
        Name = "HokkaidoNandokuQuizCache"
      }
    }
    ```

2.  **IAMロールへの権限付与**:
    Lambda関数がこのテーブルにアクセスできるよう、IAMロール (`aws_iam_role.lambda_exec_role`) のポリシーにDynamoDBの読み書き権限 (`dynamodb:GetItem`, `dynamodb:PutItem`) を追加します。

### 2. アプリケーションコードの実装 (`src/main.py`)

1.  **`boto3` クライアントの初期化**:
    `research.md` のガイダンスに従い、`lambda_handler` の外側でDynamoDBリソースを初期化します。

2.  **キャッシュキーの生成**:
    受け取ったクイズのプロンプトからSHA256ハッシュを計算するヘルパー関数を作成します。

3.  **キャッシングロジックの組み込み**:
    -   **キャッシュ取得 (GET)**: `bedrock_client.invoke` を呼び出す前に、生成したキャッシュキーで `table.get_item` を実行します。
    -   **キャッシュ保存 (PUT)**: Bedrockから取得した選択肢を `table.put_item` で保存します。この際、`expires_at` 属性に1週間後のタイムスタンプを設定します。

## テスト方法

### ユニットテスト (`tests/test_main.py`)

`boto3` の `DynamoDB` クライアントをモック（例: `unittest.mock` や `pytest-mock` を使用）して、以下のシナリオをテストします。

1.  **キャッシュヒット**: `table.get_item` が有効なアイテムを返す場合、`bedrock_client.invoke` が呼び出されないことを確認します。
2.  **キャッシュミス**: `table.get_item` がアイテムを返さない場合、`bedrock_client.invoke` が呼び出され、その後 `table.put_item` が正しいパラメータで呼び出されることを確認します。
3.  **TTLの確認**: `table.put_item` に渡される `Item` に、正しい `expires_at` タイムスタンプが含まれていることを確認します。

### 統合テスト (AWS上)

1.  Terraformでインフラをデプロイします。
2.  デプロイされたLambda関数を同じペイロードで2回連続して実行します。
3.  CloudWatch Logsを監視し、以下の点を確認します。
    -   1回目の実行ではBedrock API呼び出しのログが出力される。
    -   2回目の実行ではBedrock API呼び出しのログが出力されず、キャッシュから読み込まれたことを示すログが出力される。
    -   2回目の実行の応答時間が1回目よりも短いことを確認します。
4.  AWSコンソールのDynamoDBテーブルビューで、アイテムが正しく保存され、`expires_at` 属性が設定されていることを確認します。
