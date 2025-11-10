# Implementation Plan: AIによるクイズ選択肢の自動生成

**Author:** Gemini
**Status:** In Progress
**Created:** 2025-11-10
**Last Updated:** 2025-11-10
**Spec:** [AIによるクイズ選択肢の自動生成](./spec.md)

## 1. Technical Context

### 1.1. Architecture

- **Frontend:** 静的なHTMLとJavaScriptで構成されるWebアプリケーション。
- **Backend:** Python (FastAPI) で構築されたAPIサーバー。
- **Data Store:** なし。クイズデータはソースコード内に静的に保持。
- **Hosting:** AWS Lambda (サーバーレス環境)

### 1.2. Key Technologies & Dependencies

- **Python:** 3.11
- **FastAPI:** Webフレームワーク
- **Boto3:** AWS SDK for Python (Amazon Bedrock連携用)
- **Uvicorn:** ASGIサーバー

### 1.3. Integrations

- **Amazon Bedrock:** 外部の生成AIサービス。不正解の選択肢を生成するためにAPIを呼び出す。

### 1.4. Security

- **Authentication/Authorization:** なし。公開API。
- **Data Security:** ユーザー入力は受け付けないため、特別な対策は不要。
- **Secrets Management:** AWS LambdaにアタッチされたIAMロールを通じてBedrockへのアクセス権限を管理する。ローカル開発環境では環境変数を利用する。

### 1.5. Testing

- **Unit Tests:** `pytest` を使用。外部APIとの連携部分はモック化する。
- **Integration Tests:** なし。
- **End-to-End Tests:** なし。

### 1.6. Open Questions & Clarifications

- **[NEEDS CLARIFICATION]** Amazon Bedrock APIの具体的なリージョンとエンドポイントURL。
- **[NEEDS CLARIFICATION]** Bedrock API呼び出し時のタイムアウト値とリトライ回数の適切な設定。
- **[NEEDS CLARIFICATION]** Bedrock APIからのエラーレスポンスの具体的なフォーマットとハンドリング方法。

## 2. Constitution Check

### 2.1. Core Principles

| Principle | Adherence | Justification |
|---|---|---|
| **User-Centric** | Yes | この機能は、AIが生成した質の高い選択肢を提供することで、ユーザーのクイズ体験を直接的に向上させることを目的としています。 |
| **Simplicity** | Yes | 既存のアーキテクチャへの変更を最小限に抑え、単一目的のAPI連携を追加するのみです。 |
| **Maintainability** | Yes | 外部APIとの連携部分を独立したモジュールとして実装し、テストを容易にします。 |
| **Scalability** | Yes | AWS Lambda上で動作させることで、スケーラビリティを確保します。 |
| **Security** | Yes | AWSの認証情報をコードに含めず、IAMロールを利用することで安全なAPI連携を実現します。 |
| **Cost-Effectiveness** | Yes | 利用するBedrockモデルは比較的低コストなものを選択しており、API呼び出しも問題表示時のみに限定されます。 |

### 2.2. Gate Evaluation

| Gate | Status | Notes |
|---|---|---|
| **Security Review** | PASS | |
| **Privacy Review** | PASS | |
| **Architecture Review** | PASS | |
| **Code Style Check** | PASS | |
| **Testing Plan** | PASS | |

## 3. Phase 0: Outline & Research

### 3.1. Research Tasks

- **Task 1:** Amazon Bedrockの公式ドキュメントを調査し、Python (Boto3) を利用したAPIの呼び出し方法、特に `anthropic.claude-haiku-4-5-20251001-v1:0` モデルの利用方法を確認する。
- **Task 2:** Bedrock APIのリージョンごとのエンドポイントURLを特定する。
- **Task 3:** API呼び出しにおける適切なタイムアウト値とリトライ戦略に関するベストプラクティスを調査する。
- **Task 4:** Bedrock APIが返すエラーレスポンスの構造を調査し、具体的なエラーハンドリングのパターンをまとめる。

### 3.2. Research Findings

- **File:** `research.md` (Phase 0完了時に作成)

## 4. Phase 1: Design & Contracts

### 4.1. Data Model

- **File:** `data-model.md` (Phase 1完了時に作成)
- **Notes:** 本機能では新たなデータモデルの追加はありません。

### 4.2. API Contracts

- **File:** `contracts/api.yaml` (Phase 1完了時に作成)
- **Notes:** 既存の `/quiz` エンドポイントのレスポンスに変更はありませんが、バックエンドの実装が変更されます。選択肢を生成するための新しい内部APIは作成しません。

### 4.3. Quickstart Guide

- **File:** `quickstart.md` (Phase 1完了時に作成)

## 5. Phase 2: Implementation & Testing

### 5.1. Implementation Tasks

- **Task 1:** Bedrock APIと通信するためのクライアントモジュールを実装する。
- **Task 2:** `/quiz` エンドポイントのロジックを修正し、問題表示時にBedrockクライアントを呼び出して不正解の選択肢を取得する。
- **Task 3:** Bedrock API呼び出しでエラーが発生した場合に、静的なダミー選択肢を返すフォールバック処理を実装する。
- **Task 4:** アプリケーションがLambda上で実行されることを想定し、Boto3が自動的にIAMロールの認証情報を使用するように設定する。ローカル開発用に環境変数からの認証情報読み込みもサポートする。
- **Task 5:** 上記の実装に対する単体テストを作成する。

### 5.2. Testing Tasks

- **Task 1:** Bedrock APIが正常にレスポンスを返す場合の単体テストを実装する。
- **Task 2:** Bedrock APIがエラーを返す場合の単体テストを実装する (モックを使用)。
- **Task 3:** Bedrock APIがタイムアウトする場合の単体テストを実装する (モックを使用)。

## 6. Phase 3: Deployment & Release

### 6.1. Deployment Plan

- (TBD)

### 6.2. Release Plan

- (TBD)
