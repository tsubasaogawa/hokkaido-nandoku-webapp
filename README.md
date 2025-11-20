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

## デプロイ

このアプリケーションはTerraformを使用してAWSにデプロイされます。

1.  **Terraformの作業ディレクトリに移動します:**
    ```bash
    cd terraform
    ```

2.  **Terraformを初期化します:**
    ```bash
    terraform init
    ```

3.  **デプロイ計画を確認します:**
    ```bash
    terraform plan -var "api_endpoint=<YOUR_API_ENDPOINT>"
    ```
    `<YOUR_API_ENDPOINT>` を、`hokkaido-nandoku-api`のデプロイ済みエンドポイントURLに置き換えてください。

4.  **リソースを適用（デプロイ）します:**
    ```bash
    terraform apply -var "api_endpoint=<YOUR_API_ENDPOINT>" -auto-approve
    ```

デプロイが完了すると、`lambda_function_url`という名前の出力が表示されます。これがクイズアプリケーションのURLです。

## 実行

Terraformのデプロイ出力で得られたURLにWebブラウザでアクセスすると、クイズをプレイできます。