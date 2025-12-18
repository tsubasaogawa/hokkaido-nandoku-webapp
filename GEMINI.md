# hokkaido-nandoku-webapp Development Guidelines

Auto-generated from all feature plans. Last updated: 2025-11-07

## Active Technologies

- (001-hokkaido-nandoku-quiz)

## Project Structure

```text
src/
tests/
```

## Commands

# Add commands for 

## Code Style

: Follow standard conventions

## Recent Changes

- 001-hokkaido-nandoku-quiz: Added

<!-- MANUAL ADDITIONS START -->
## デプロイ方法

このWebアプリケーションをAWS Lambdaにデプロイする手順は以下の通りです。

1.  **Pythonの依存関係をインストールし、デプロイパッケージを作成します:**
    `src` ディレクトリのコードと、必要なPythonライブラリ (`jinja2`, `python-multipart`) を `dist` ディレクトリにパッケージングします。Lambda の実行環境と互換性のあるバイナリをインストールするため、`--platform` オプションを使用します。
    ```bash
    rm -rf dist/*
    pip install . jinja2 python-multipart -t dist --platform manylinux2014_x86_64 --python-version 3.13 --only-binary=:all:
    cp -r src/* dist/
    cp -r templates dist/
    ```

2.  **Terraformの作業ディレクトリに移動します:**
    ```bash
    cd terraform
    ```

3.  **Terraformを初期化します:**
    ```bash
    terraform init
    ```

4.  **リソースを適用（デプロイ）します:**
    `api_endpoint` 変数には、`hokkaido-nandoku-api` のデプロイ済みエンドポイントURL（例: `https://ecif1srlak.execute-api.ap-northeast-1.amazonaws.com`）を指定します。
    ```bash
    terraform apply -var "api_endpoint=<YOUR_API_ENDPOINT>" -auto-approve
    ```
    デプロイが完了すると、`lambda_function_url`という名前の出力が表示されます。これがクイズアプリケーションのURLです。

## 動作確認方法

デプロイ後、アプリケーションが正しく動作しているかを確認します。

1.  **`curl` を利用したサイトアクセス確認:**
    デプロイ出力で得られた `lambda_function_url` （例: `https://hcflplibhd3ea3ktlsxwfaenke0kwrmq.lambda-url.ap-northeast-1.on.aws/`）に対して `curl` コマンドで HTTP GET リクエストを実行します。
    ```bash
    curl -X GET https://hcflplibhd3ea3ktlsxwfaenke0kwrmq.lambda-url.ap-northeast-1.on.aws/
    ```
    正常に動作していれば、HTMLコンテンツが返され、その中に `quizData` を含むJavaScriptの定義（例: `const quizData = {"correct_answer": "そうべつ", ...};`）が含まれているはずです。

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
