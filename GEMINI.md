# hokkaido-nandoku-webapp Development Guidelines

Auto-generated from all feature plans. Last updated: 2025-11-07

## Active Technologies
- Python 3.13 (Backend), HTML5/CSS3/ES6+ (Frontend) + FastAPI (Backend)
- DynamoDB (Caching)
- CloudFront (CDN)
- API Gateway (HTTP API)
- Terraform (IaC with Modules)

- (001-hokkaido-nandoku-quiz)

## Project Structure

```text
src/
tests/
terraform/
  modules/
    api_gateway/
    cloudfront/
    dynamodb/
```

## Commands

# Add commands for 

## Code Style

: Follow standard conventions

## Recent Changes
- Refactored infrastructure to use Terraform modules
- Implemented CloudFront -> API Gateway -> Lambda architecture
- Added X-CF-Secret header verification for security
- 004-modern-quiz-ui: Added Python 3.13 (Backend), HTML5/CSS3/ES6+ (Frontend) + FastAPI (Backend)


<!-- MANUAL ADDITIONS START -->
## デプロイ方法

このWebアプリケーションをAWSにデプロイする手順は以下の通りです。
TerraformモジュールがPythonの依存関係インストールとパッケージングを自動的に行います（Dockerが必要です）。

1.  **Terraformの作業ディレクトリに移動します:**
    ```bash
    cd terraform
    ```

2.  **Terraformを初期化します:**
    ```bash
    terraform init
    ```

3.  **リソースを適用（デプロイ）します:**
    `api_endpoint` 変数には、`hokkaido-nandoku-api` のデプロイ済みエンドポイントURL（例: `ecif1srlak.execute-api.ap-northeast-1.amazonaws.com`）を指定します。
    ```bash
    terraform apply -var "api_endpoint=<YOUR_API_ENDPOINT>" -auto-approve
    ```
    デプロイが完了すると、`cloudfront_url`という名前の出力が表示されます。これがクイズアプリケーションのURLです。

## 動作確認方法

デプロイ後、アプリケーションが正しく動作しているかを確認します。

1.  **`curl` を利用したサイトアクセス確認:**
    デプロイ出力で得られた `cloudfront_url` （例: `d2m20hq82lg8zn.cloudfront.net`）に対して `curl` コマンドで HTTP GET リクエストを実行します。
    ```bash
    curl -v https://<YOUR_CLOUDFRONT_URL>/
    ```
    正常に動作していれば、HTMLコンテンツが返され、その中に `quizData` を含むJavaScriptの定義（例: `const quizData = {"correct_answer": "そうべつ", ...};`）が含まれているはずです。
    
    なお、セキュリティ設定により、CloudFrontを経由しない直接アクセス（API Gatewayへのアクセスなど）は `403 Forbidden` となります。

2.  **エラー発生時の CloudWatch Logs 参照:**
    `curl` の結果が `Internal Server Error` などであった場合、AWS CloudWatch Logs を参照して詳細なエラー原因を特定します。

    *   **ロググループの特定**:
        Lambda 関数のログは、`/aws/lambda/hokkaido-nandoku-quiz` というロググループに保存されます。

    *   **最新のログストリーム名の取得**:
        以下の AWS CLI コマンドで、最新のログストリーム名を取得します。
        ```bash
        aws logs describe-log-streams --log-group-name /aws/lambda/hokkaido-nandoku-quiz --order-by LastEventTime --descending --limit 1 --query 'logStreams[0].logStreamName' --output text
        ```

    *   **ログイベントの取得**:
        取得したログストリーム名を使用して、最新のログイベントを取得します。
        ```bash
        aws logs get-log-events --log-group-name /aws/lambda/hokkaido-nandoku-quiz --log-stream-name '<取得したログストリーム名>' --limit 50
        ```
        これにより、エラーメッセージやスタックトレースなど、問題解決の手がかりとなる情報が得られます。
<!-- MANUAL ADDITIONS END -->
