

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
