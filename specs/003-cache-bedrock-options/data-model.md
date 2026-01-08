# Data Model: Quiz Option Cache

このドキュメントでは、Bedrockによって生成されたクイズの選択肢をキャッシュするためのDynamoDBテーブルのスキーマを定義します。

## DynamoDB Table: `hokkaido-nandoku-quiz-cache`

### Attributes

| Attribute Name | Type | Description |
| :--- | :--- | :--- |
| `cache_key` | String (S) | **Partition Key**. クイズの問題文（漢字）のSHA256ハッシュ。 |
| `options` | List (L) | Bedrockによって生成された誤選択肢のリスト。 |
| `expires_at` | Number (N) | **TTL Attribute**. アイテムが失効するUnixタイムスタンプ（作成から1週間後）。 |

### Key Schema

- **Partition Key**: `cache_key`

### Billing Mode

- `PAY_PER_REQUEST` (オンデマンド)

### Time to Live (TTL)

- 属性名 `expires_at` で有効化。