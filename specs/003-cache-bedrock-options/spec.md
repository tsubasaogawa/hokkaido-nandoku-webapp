# Feature Specification: Bedrock選択肢のDynamoDBキャッシング

**Feature Branch**: `003-cache-bedrock-options`
**Created**: 2026-01-08
**Status**: Draft
**Input**: User description: "Bedrock によって生成された選択肢を DynamoDB にキャッシングさせるようにしたい。DynamoDB には TTL を設定し、デフォルト 1 週間ごとにアイテムが消えるようにすること。"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - キャッシュを利用した選択肢取得 (Priority: P1)

ユーザーがクイズを開始した際、アプリケーションはまずDynamoDBにキャッシュされた選択肢がないか確認します。キャッシュが存在すればそれを返し、なければBedrock APIを呼び出して取得した上でキャッシュに保存し、ユーザーに返します。これにより、APIコストの削減と応答速度の向上が期待できます。

**Why this priority**: この機能はアプリケーションのパフォーマンスと運用コストに直接影響を与えるため、最優先とします。

**Independent Test**: 同じクイズに対して複数回アクセスし、2回目以降のアクセスで応答時間が短縮され、かつBedrock APIへのリクエストが発生しないことを確認することでテスト可能です。

**Acceptance Scenarios**:

1.  **Given** 特定のクイズIDに対するキャッシュがDynamoDBに存在しない, **When** ユーザーがそのクイズを要求する, **Then** システムはBedrock APIを呼び出して選択肢を生成し、DynamoDBにTTL（1週間）付きで保存し、ユーザーに選択肢を返す
2.  **Given** 特定のクイズIDに対する有効なキャッシュがDynamoDBに存在する, **When** ユーザーがそのクイズを要求する, **Then** システムはBedrock APIを呼び出さず、DynamoDBから直接選択肢を取得してユーザーに返す
3.  **Given** 特定のクイズIDに対するキャッシュがDynamoDBに存在するがTTLが切れている, **When** ユーザーがそのクイズを要求する, **Then** システムはBedrock APIを呼び出して選択肢を再生成し、DynamoDBのキャッシュを更新し、ユーザーに新しい選択肢を返す

### Edge Cases

- Bedrock APIがエラーを返した場合、システムはどのように振る舞うか？ → キャッシュは作成せず、エラーをログに記録し、ユーザーにはエラーメッセージを表示すべき。
- DynamoDBへの書き込みに失敗した場合、どうするか？ → 選択肢はユーザーに返すが、キャッシュはされない。エラーはログに記録する。

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: システムは、Bedrockによって生成されたクイズの選択肢をDynamoDBテーブルにキャッシュしなければならない。
- **FR-002**: キャッシュアイテムには、キーとしてクイズを一意に識別するIDを持たなければならない。
- **FR-003**: キャッシュアイテムには、TTL（Time To Live）属性を設定しなければならない。
- **FR-004**: TTLのデフォルト値は、アイテム作成時から1週間（604800秒）でなければならない。
- **FR-005**: キャッシュが存在しない（キャッシュミス）場合、システムはBedrock APIからデータを取得し、キャッシュを更新しなければならない。
- **FR-006**: キャッシュが存在する（キャッシュヒット）場合、システムはBedrock APIを呼び出さずにキャッシュからデータを返さなければならない。

### Key Entities

- **QuizOptionCache**: Bedrockが生成した選択肢のキャッシュ情報を表すエンティティ。
  - `cache_key` (Partition Key): キャッシュを特定するための一意なキー（例：クイズ問題のテキストやID）。
  - `options`: Bedrockが生成した選択肢のデータ。
  - `expires_at` (TTL Attribute): アイテムの有効期限を示すUnixタイムスタンプ。

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: キャッシュヒット時の平均応答時間は、キャッシュミス時（Bedrock API呼び出しを含む）と比較して、50%以上短縮されること。
- **SC-002**: 同じクイズに対する2回目以降のリクエストでは、Bedrock APIへのコールが99%削減されること。
- **SC-003**: DynamoDBに保存されたキャッシュアイテムは、作成から正確に1週間後に自動的に削除されること。
- **SC-004**: 機能導入後、Bedrock APIの利用コストが20%以上削減されること。