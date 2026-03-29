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

### 実装済み API

- `GET /api/v1/health`
- `CRUD /api/v1/athletes`
- `CRUD /api/v1/videos`
- `CRUD /api/v1/analysis-sessions`
- `CRUD /api/v1/analysis-sessions/{session_id}/tracks`
- `CRUD /api/v1/tracks/{track_id}/points`

### ローカル検証コマンド

バックエンドを起動したあと、別ターミナルで次を実行すると最小限の疎通確認ができます。

```bash
curl http://127.0.0.1:8000/api/v1/health
```

`athletes` を作成する前に、参照先となる `organizations` を1件入れておくと検証がスムーズです。

```bash
psql -d sports_analytics -c "INSERT INTO organizations (id, name, slug, plan_type, created_at, updated_at) VALUES ('00000000-0000-0000-0000-000000000001', 'Demo Organization', 'demo-org', 'free', NOW(), NOW()) ON CONFLICT (slug) DO NOTHING;"
```

```bash
curl -X POST http://127.0.0.1:8000/api/v1/athletes \
  -H 'Content-Type: application/json' \
  -d '{
    "organization_id": "00000000-0000-0000-0000-000000000001",
    "team_id": null,
    "external_code": "ATH-001",
    "name": "テスト選手",
    "kana_name": "テストセンシュ",
    "birth_date": null,
    "sex": null,
    "dominant_side": "right",
    "position_name": "RW",
    "height_cm": null,
    "weight_kg": null,
    "note": "README検証用"
  }'
```

```bash
curl http://127.0.0.1:8000/api/v1/athletes
```

補足: `POST /api/v1/athletes` は、事前に `organizations` テーブルへ対象IDのレコードが入っている前提です。初回は `health` 確認後に上の `INSERT` を実行してから `athletes` の検証へ進むのが安全です。
