## セットアップ

### 前提条件

- Python 3.13+
- Terraform 1.0+
- AWS アカウントと設定済みの認証情報

### ローカル開発時の AWS 認証情報

このアプリケーションは AWS Lambda 上での実行を想定しており、IAM ロールによって Bedrock へのアクセス権限が付与されます。

### 手順

1.  **リポジトリをクローンします:**
    ```bash
    git clone https://github.com/tsubasaogawa/hokkaido-nandoku-webapp.git
    cd hokkaido-nandoku-webapp
    ```

2.  **Pythonの依存関係をインストールします:**
    ```bash
    uv pip install -r requirements.txt
    ```
    (事前に `uv` のインストールが必要です)

## ログ調査によるデバッグ方法

AWS Lambda 関数で問題が発生した場合、CloudWatch Logs を確認することが最も効果的なデバッグ方法です。

1.  **ロググループの特定**:
    Lambda 関数のログは、通常 `/aws/lambda/<関数名>` というロググループに保存されます。このアプリケーションの場合、ロググループ名は `/aws/lambda/hokkaido-nandoku-quiz` です。

2.  **最新のログストリームの取得**:
    以下の AWS CLI コマンドで、最新のログストリーム名を取得します。
    ```bash
    aws logs describe-log-streams --log-group-name /aws/lambda/hokkaido-nandoku-quiz --order-by LastEventTime --descending --limit 1 --query 'logStreams[0].logStreamName' --output text
    ```

3.  **ログイベントの取得**:
    取得したログストリーム名を使用して、最新のログイベントを取得します。
    ```bash
    aws logs get-log-events --log-group-name /aws/lambda/hokkaido-nandoku-quiz --log-stream-name '<取得したログストリーム名>' --limit 20
    ```
    これにより、エラーメッセージやスタックトレースなど、問題解決の手がかりとなる情報が得られます。

## デプロイ手順

このアプリケーションは Terraform を使用してAWSにデプロイされます。

1.  **Python の依存関係をインストールし、デプロイパッケージを作成します**:
    `src` ディレクトリのコードと、必要な Python ライブラリを `dist` ディレクトリにパッケージングします。Lambda の実行環境と互換性のあるバイナリをインストールするため、`--platform` オプションを使用します。
    ```bash
    mkdir -p dist
    rm -rf dist/*
    pip install . jinja2 python-multipart -t dist --platform manylinux2014_x86_64 --python-version 3.13 --only-binary=:all:
    cp -r src/* dist/
    cp -r templates dist/
    ```

2.  **Terraform の作業ディレクトリに移動します**:
    ```bash
    cd terraform
    ```

3.  **Terraform を初期化します**:
    ```bash
    terraform init
    ```

4.  **デプロイ計画を確認します**:
    `api_endpoint` 変数には、`hokkaido-nandoku-api` のデプロイ済みエンドポイント URL（例: `ecif1srlak.execute-api.ap-northeast-1.amazonaws.com`）を指定します。末尾の `/random` は含めないでください。
    ```bash
    terraform plan -var "api_endpoint=<YOUR_API_ENDPOINT>"
    ```

5.  **リソースを適用（デプロイ）します**:
    ```bash
    terraform apply -var "api_endpoint=<YOUR_API_ENDPOINT>" -auto-approve
    ```

デプロイが完了すると、`lambda_function_url`という名前の出力が表示されます。これがクイズアプリケーションの URL です。

## 実行

Terraform のデプロイ出力で得られた URL に Web ブラウザでアクセスすると、クイズをプレイできます。