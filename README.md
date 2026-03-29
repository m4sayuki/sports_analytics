# Handball Play Analysis App

ハンドボールの試合や練習を記録し、プレー傾向を素早く振り返るためのMVPプロトタイプです。

## MVPの目的

- 試合中のイベントを素早く記録できる
- 得点、失点、シュート成功率、ターンオーバーなどを即時に見える化する
- タイムラインから試合の流れを振り返れる
- 後から本格的な分析機能へ拡張しやすい土台を作る

## 想定ユーザー

- 学校部活のマネージャー
- クラブチームのコーチ
- 選手自身のセルフレビュー用途

## MVPに含める機能

1. 試合情報の入力
2. イベント記録
3. リアルタイム集計
4. タイムライン表示
5. メモ保存

## 記録する主なイベント

- 得点
- 失点
- シュート成功
- シュート失敗
- アシスト
- スティール
- セーブ
- ターンオーバー
- 退場
- タイムアウト

## 今後の拡張候補

- 選手別スタッツ
- シュート位置ヒートマップ
- 攻撃パターン分析
- 守備システム別の失点傾向
- 動画タイムスタンプ連携
- CSV / JSON エクスポート
- SupabaseやFirebaseを使ったクラウド保存
- モバイル向けPWA対応

## ファイル構成

- `index.html`: 画面構成
- `styles.css`: 見た目
- `app.js`: 記録、集計、保存処理

## 次のおすすめ

- React + TypeScript に移行
- ローカル保存をDB保存へ変更
- 選手登録と試合履歴一覧を追加


## S3へのアップロード

静的ファイルをAWS S3へアップロードするためのスクリプトを追加しています。

### 追加したファイル

- `scripts/deploy-s3.sh`: `index.html` `styles.css` `app.js` をS3へアップロード

### 前提

- AWS CLI がインストールされていること
- `aws configure` などで認証情報が設定されていること
- アップロード先バケットが作成済みであること

### 使い方

```bash
chmod +x ./scripts/deploy-s3.sh
./scripts/deploy-s3.sh your-bucket-name
```

環境変数でも指定できます。

```bash
export S3_BUCKET=your-bucket-name
export AWS_REGION=ap-northeast-1
export S3_PREFIX=motion-view
./scripts/deploy-s3.sh
```

### 補足

- `index.html` は更新が反映されやすいように `no-cache` 系のヘッダーでアップロードします
- `styles.css` と `app.js` も同様に保守しやすい設定でアップロードします
- S3をWeb公開する場合は、別途バケットポリシーや静的ホスティング設定が必要です

## バックエンド

`backend/` 配下に FastAPI ベースのバックエンド実装を追加しています。

### 主な構成

- `backend/app/main.py`: FastAPI アプリ起動点
- `backend/app/models/`: SQLAlchemy モデル
- `backend/app/schemas/`: Pydantic スキーマ
- `backend/app/api/v1/routers/`: CRUD ルーター
- `backend/alembic/`: Alembic 設定と初期マイグレーション
- `backend/requirements.txt`: Python 依存関係
- `backend/Dockerfile`: 本番コンテナ定義
- `backend/apprunner.yaml`: App Runner 用設定ひな形

### セットアップ

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

### 起動

```bash
uvicorn app.main:app --reload
```

### マイグレーション

```bash
alembic upgrade head
```

### Docker 起動

```bash
docker build -t sports-analytics-api ./backend
docker run --rm -p 8000:8000 --env-file ./backend/.env.production.example sports-analytics-api
```

### ローカル Docker 検証

Docker Desktop を起動したうえで、`backend/.env.docker.local.example` をコピーして使います。

```bash
cd /Users/mitamasasuke/workspace/sports_analytics/backend
cp .env.docker.local.example .env.docker.local
docker build -t sports-analytics-api .
docker run --rm -p 8000:8000 --env-file ./.env.docker.local sports-analytics-api
```

補足: コンテナからホストMacの PostgreSQL に接続するため、`DATABASE_URL` は `host.docker.internal` を使っています。

### App Runner 想定

- Container Port: `8000`
- Health Check Path: `/api/v1/health`
- 本番環境変数は `backend/.env.production.example` をベースに設定

### 実装済み API

- `GET /api/v1/health`
- `CRUD /api/v1/athletes`
- `CRUD /api/v1/videos`
- `CRUD /api/v1/analysis-sessions`
- `CRUD /api/v1/analysis-sessions/{session_id}/tracks`
- `CRUD /api/v1/tracks/{track_id}/points`


### 確認済みデプロイ先

- App Runner URL: `https://dzmbuju8pw.ap-northeast-1.awsapprunner.com`
- Health Check: `https://dzmbuju8pw.ap-northeast-1.awsapprunner.com/api/v1/health`
