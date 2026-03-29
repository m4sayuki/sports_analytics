

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

```bash
cd /Users/mitamasasuke/workspace/sports_analytics/backend
cp .env.docker.local.example .env.docker.local
docker build -t sports-analytics-api .
docker run --rm -p 8000:8000 --env-file ./.env.docker.local sports-analytics-api
```

補足: `DATABASE_URL` は `host.docker.internal` を使ってホストMac上の PostgreSQL に接続します。

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
