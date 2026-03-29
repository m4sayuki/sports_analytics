# App Runner / App Store デプロイ手順

## バックエンド

対象ディレクトリ: `backend/`

追加済みファイル:
- `backend/Dockerfile`
- `backend/.dockerignore`
- `backend/start.sh`
- `backend/.env.production.example`
- `backend/apprunner.yaml`

### ECR へイメージを作成して push

```bash
cd /Users/mitamasasuke/workspace/sports_analytics/backend
docker build -t sports-analytics-api .
```

その後、ECR リポジトリへ push して App Runner のソースに指定します。

### App Runner 自動デプロイスクリプト

```bash
cd /Users/mitamasasuke/workspace/sports_analytics/backend
RUN_MIGRATIONS_ON_STARTUP=false ./scripts/deploy_apprunner.sh
```

Apple Silicon Mac からは `linux/amd64` イメージで push する必要があるため、スクリプト側で `DOCKER_PLATFORM=linux/amd64` を既定化しています。

`DATABASE_URL` などを事前に export しておくと、そのまま App Runner の環境変数へ反映されます。DB 未作成の段階では `RUN_MIGRATIONS_ON_STARTUP=false` のままデプロイし、`/api/v1/health` の疎通確認を先に行うのが安全です。

### App Runner で設定する代表値

- Port: `8000`
- Health check path: `/api/v1/health`
- Start command: `sh start.sh`

### 本番環境変数

`.env.production.example` をベースに次を設定します。

- `DATABASE_URL`
- `SECRET_KEY`
- `ACCESS_TOKEN_EXPIRE_MINUTES`
- `CORS_ORIGINS`
- `APP_ENV=production`

### 補足

`start.sh` は起動時に `alembic upgrade head` を実行してから `uvicorn` を起動します。DB マイグレーションを別ジョブに分離したい場合は、後から切り出せます。

## Flutter

対象ディレクトリ: `sports_analytics_flutter/`

追加済みファイル:
- `lib/flavors.dart`
- `lib/main_dev.dart`
- `lib/main_staging.dart`
- `lib/main_prod.dart`

### ローカル開発

```bash
cd /Users/mitamasasuke/workspace/sports_analytics_flutter
/Users/mitamasasuke/workspace/flutter/bin/flutter run -t lib/main_dev.dart
```

### ステージング

```bash
/Users/mitamasasuke/workspace/flutter/bin/flutter run \
  -t lib/main_staging.dart \
  --dart-define=API_BASE_URL=https://staging-api.example.com
```

### 本番

```bash
/Users/mitamasasuke/workspace/flutter/bin/flutter build ios \
  -t lib/main_prod.dart \
  --dart-define=API_BASE_URL=https://api.example.com
```

### 接続先の考え方

- `dev`: 端末に応じたローカルURLを自動使用
- `staging`: ステージングAPIを利用
- `prod`: App Store 提出用の本番APIを利用

### App Store 提出前の確認

- 本番ビルドは `https` のみを使う
- `API Base URL` を画面で変更しなくても動く値を `--dart-define` で渡す
- 実機で動画アップロードと API 接続を確認する


### 確認済みデプロイ先

- App Runner URL: `https://dzmbuju8pw.ap-northeast-1.awsapprunner.com`
- Health Check: `https://dzmbuju8pw.ap-northeast-1.awsapprunner.com/api/v1/health`
