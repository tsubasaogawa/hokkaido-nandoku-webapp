# Actionable Tasks: 北海道難読地名クイズ (SPA Version)

**Feature**: `001-hokkaido-nandoku-quiz`
**Generated**: 2025-11-07
**Spec**: [北海道難読地名クイズ](./spec.md)

## Phase 1: Setup

- [X] T001 `pyproject.toml`ファイルを作成し、`requests`ライブラリを依存関係として追加します。
- [X] T002 `.gitignore`ファイルを更新し、Pythonの一般的な除外設定（例: `__pycache__/`, `*.pyc`, `.venv/`）を追加します。
- [X] T003 `main.py`ファイルを作成し、基本的なLambdaハンドラ関数を設置します。
- [X] T004 `templates/`ディレクトリを作成し、SPAのメインページとなる`index.html`ファイルを追加します。
- [X] T005 `terraform/`ディレクトリを作成し、Lambda関数とFunction URLを定義する基本的なTerraform設定（`main.tf`, `variables.tf`, `outputs.tf`）を初期化します。

## Phase 2: Foundational Tasks

- [X] T006 `main.py`で、環境変数`NANDOKU_API_ENDPOINT`を読み込み、設定されていない場合はエラーを発生させるロ-ジックを実装します。
- [X] T007 `main.py`に、バックエンドAPIからクイズデータを取得するための関数（例: `get_quiz_data()`）を実装します。

## Phase 3: User Story 1 - クイズをプレイする

**Goal**: ユーザーは単一のページでクイズに回答し、ページ遷移なしで結果を確認し、次の問題に進むことができます。
**Independent Test**: ユーザーは、デプロイされたLambda Function URLにアクセスし、クイズをプレイして正解・不正解の結果を動的に確認できる必要があります。

- [X] T008 [US1] `main.py`のLambdaハンドラを更新し、GETリクエストに対して`templates/index.html`をレンダリングして返却するようにします。その際、`get_quiz_data()`を呼び出して取得したクイズ情報をテンプレートに渡します。
- [X] T009 [US1] `templates/index.html`を更新し、受け取ったクイズデータ（地名と選択肢）を表示するフォームと、結果表示用の領域（例: `<div id="result"></div>`）を作成します。
- [X] T010 [US1] `main.py`のLambdaハンドラを更新し、POSTリクエストを処理できるようにします。ユーザーの回答とクイズのIDを受け取り、正解かどうかを判定します。
- [X] T011 [US1] `main.py`のPOSTリクエストハンドラを修正し、HTMLをレンダリングする代わりに、判定結果（例: `{"result": "correct"}` または `{"result": "incorrect", "correct_answer": "..."}`）をJSON形式で返却するようにします。
- [X] T012 [US1] `templates/index.html`にJavaScriptを追加します。このスクリプトは、フォームの送信をインターセプトし、`fetch` APIを使用して非同期でPOSTリクエストをバックエンドに送信します。
- [X] T013 [US1] `templates/index.html`のJavaScriptを更新し、バックエンドから受け取ったJSONレスポンスに基づいて、結果表示用の領域のDOMを動的に書き換え、「正解」または「不正解」と正解の答えを表示するようにします。
- [X] T014 [US1] `templates/index.html`に「次の問題へ」ボタンを追加し、クリックされるとページをリロードして新しいクイズを取得するJavaScriptのロジックを実装します。

## Phase 4: Polish & Cross-Cutting Concerns

- [ ] T015 APIリクエストが失敗した場合のエラーハンドリングを`main.py`に実装し、JSON形式でエラーメッセージを返すようにします。また、フロントエンドのJavaScriptでそのエラーをハンドリングし、ユーザーにエラーメッセージを表示します。
- [ ] T016 `README.md`ファイルを更新し、アプリケーションのセットアップ、デプロイ、および使用方法に関する詳細な手順を記載します。
- [ ] T017 Terraformの`main.tf`を更新し、`NANDOKU_API_ENDPOINT`環境変数をLambda関数に渡す設定を追加します。

## Dependencies

- **User Story 1**は、**Foundational Tasks**に依存します。

## Parallel Execution

- **Phase 1**のタスク（T001-T005）は、それぞれ独立しているため、並行して実行可能です。
- **Phase 3**では、フロントエンド（HTML/JavaScript）とバックエンド（`main.py`）の実装を並行して進めることができます。
  - T009, T012, T013, T014（フロントエンド）
  - T008, T010, T011（バックエンド）

## Implementation Strategy

最初にMVP（Minimum Viable Product）としてUser Story 1を完成させ、基本的なクイズ機能を提供します。その後、エラーハンドリングやドキュメントの整備などの改善を行います。
