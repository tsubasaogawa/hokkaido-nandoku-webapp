# 北海道難読地名クイズ Webアプリケーション

これは、北海道の難読地名の読み方を当てるクイズを提供するWebアプリケーションです。AWS LambdaとTerraformを使用して構築されています。

## 概要

ユーザーはWebページにアクセスすると、ランダムに選ばれた北海道の難読地名と4つの読み方の選択肢が表示されます。回答を選択すると、正解・不正解が即座に表示され、次の問題に進むことができます。

バックエンドAPIとして [hokkaido-nandoku-api](https://github.com/tsubasaogawa/hokkaido-nandoku-api) を利用しています。

## セットアップ

### 前提条件

- Python 3.13+
- Terraform 1.0+
- AWSアカウントと設定済みの認証情報

### ローカル開発時のAWS認証情報

このアプリケーションはAWS Lambda上での実行を想定しており、IAMロールによってBedrockへのアクセス権限が付与されます。

ローカルで開発・テストを行う場合は、以下の環境変数を設定してください。

```bash
export AWS_ACCESS_KEY_ID="YOUR_ACCESS_KEY"
export AWS_SECRET_ACCESS_KEY="YOUR_SECRET_KEY"
export AWS_SESSION_TOKEN="YOUR_SESSION_TOKEN" # (Optional)
export AWS_DEFAULT_REGION="ap-northeast-1"
```

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

このアプリケーションはTerraformを使用してAWSにデプロイされます。

1.  **Pythonの依存関係をインストールし、デプロイパッケージを作成します**:
    `src` ディレクトリのコードと、必要なPythonライブラリを `dist` ディレクトリにパッケージングします。Lambda の実行環境と互換性のあるバイナリをインストールするため、`--platform` オプションを使用します。
    ```bash
    rm -rf dist/*
    pip install . jinja2 python-multipart -t dist --platform manylinux2014_x86_64 --python-version 3.13 --only-binary=:all:
    cp -r src/* dist/
    cp -r templates dist/
    ```

2.  **Terraformの作業ディレクトリに移動します**:
    ```bash
    cd terraform
    ```

3.  **Terraformを初期化します**:
    ```bash
    terraform init
    ```

4.  **デプロイ計画を確認します**:
    `api_endpoint` 変数には、`hokkaido-nandoku-api` のデプロイ済みエンドポイントURL（例: `ecif1srlak.execute-api.ap-northeast-1.amazonaws.com`）を指定します。末尾の `/random` は含めないでください。
    ```bash
    terraform plan -var "api_endpoint=<YOUR_API_ENDPOINT>"
    ```

5.  **リソースを適用（デプロイ）します**:
    ```bash
    terraform apply -var "api_endpoint=<YOUR_API_ENDPOINT>" -auto-approve
    ```

デプロイが完了すると、`lambda_function_url`という名前の出力が表示されます。これがクイズアプリケーションのURLです。

## 実行

Terraformのデプロイ出力で得られたURLにWebブラウザでアクセスすると、クイズをプレイできます。