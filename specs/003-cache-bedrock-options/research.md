# Research: Bedrock選択肢のDynamoDBキャッシング

このドキュメントは、Bedrockが生成したクイズ選択肢をDynamoDBにキャッシュする機能の実装に向けた技術的な調査結果をまとめたものです。

## 1. DynamoDBパーティションキー戦略

**課題**: キャッシュされたアイテムを一意に識別し、効率的にアクセスするためのパーティションキー（仕様書の`cache_key`）をどう設計するか。

**決定**:
クイズ生成のプロンプトとして使用される **質問テキストを正規化（小文字化、前後の空白削除）し、そのSHA256ハッシュ値をパーティションキーとして使用** します。

**根拠**:
- **一意性と決定性**: 同じ質問からは常に同じハッシュが生成されるため、キャッシュの検索と更新が確実に行えます。
- **キーの効率性**: ハッシュ値は固定長であり、DynamoDBのキー長制限やパフォーマンス上の問題を回避できます。生のテキストをキーにすると、長文の場合に問題が発生する可能性があります。
- **堅牢性**: 質問テキストの僅かな違い（例：大文字小文字、空白）がキャッシュミスを引き起こすのを防ぎます。

**代替案**:
- **生の質問テキスト**: キーの長さが不定で、特殊文字が含まれる可能性があり、DynamoDBのベストプラクティスに反します。
- **UUID**: 決定論的でないため、同じ質問に対してキャッシュをヒットさせることができません。

## 2. DynamoDB TTLの実装

**課題**: 仕様書で要求されている「1週間の有効期限」をDynamoDBでどのように実現するか。

**決定**:
DynamoDBの標準TTL機能を利用します。
1.  TerraformでDynamoDBテーブルを定義する際に、TTLを有効化し、TTL属性名を `expires_at` に設定します。
2.  アプリケーションコード（Python）でアイテムを保存する際、現在のUnixタイムスタンプにTTLの秒数（1週間 = 604,800秒）を加算した値を `expires_at` 属性としてアイテムに含めます。

**根拠**:
これはDynamoDBが公式にサポートする標準的な方法であり、追加のクリーンアップ処理を実装する必要がなく、コスト効率にも優れています。

**実装サンプル (Terraform)**:
```terraform
resource "aws_dynamodb_table" "cache_table" {
  # ... (name, hash_key, etc.)
  ttl {
    attribute_name = "expires_at"
    enabled        = true
  }
}
```

**実装サンプル (Python/boto3)**:
```python
import time

# 1週間のTTL
ttl_seconds = 7 * 24 * 60 * 60
expires_at = int(time.time()) + ttl_seconds

item = {
    'cache_key': 'your_sha256_hash',
    'options': ['選択肢1', '選択肢2'],
    'expires_at': expires_at  # Unixタイムスタンプ（数値型）
}
table.put_item(Item=item)
```

## 3. Boto3クライアントの初期化

**課題**: AWS Lambda関数内で`boto3`クライアントをいつ、どのように初期化するのが最も効率的か。

**決定**:
DynamoDBにアクセスするための **`boto3`クライアント（またはリソース）は、Lambdaハンドラ関数の外側、つまりグローバルスコープで初期化** します。

**根拠**:
AWS Lambdaは実行環境を再利用する特性があります。クライアントをグローバルスコープで初期化することで、後続の関数呼び出し時にTCP接続が再利用され、処理のレイテンシーが短縮されます。ハンドラ内で毎回初期化するのは非効率です。

**実装サンプル (Python)**:
```python
import boto3

# グローバルスコープでクライアントを初期化
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('YourTableName')

def lambda_handler(event, context):
    # この中ではクライアントを初期化せず、グローバル変数 `table` を使用する
    # ...
    response = table.get_item(Key={'cache_key': 'some_key'})
    # ...
```
