#!/usr/bin/env bash
set -euo pipefail

AWS_REGION="${AWS_REGION:-ap-northeast-1}"
ACCOUNT_ID="${ACCOUNT_ID:-$(aws sts get-caller-identity --query Account --output text)}"
ECR_REPOSITORY="${ECR_REPOSITORY:-sports-analytics-api}"
APP_RUNNER_SERVICE_NAME="${APP_RUNNER_SERVICE_NAME:-sports-analytics-api}"
APP_RUNNER_ACCESS_ROLE_NAME="${APP_RUNNER_ACCESS_ROLE_NAME:-AppRunnerECRAccessRole}"
IMAGE_TAG="${IMAGE_TAG:-$(date +%Y%m%d%H%M%S)}"
PORT="${PORT:-8000}"
RUN_MIGRATIONS_ON_STARTUP="${RUN_MIGRATIONS_ON_STARTUP:-false}"
AUTO_DEPLOYMENTS_ENABLED="${AUTO_DEPLOYMENTS_ENABLED:-false}"
CPU="${APP_RUNNER_CPU:-1 vCPU}"
MEMORY="${APP_RUNNER_MEMORY:-2 GB}"
DOCKER_PLATFORM="${DOCKER_PLATFORM:-linux/amd64}"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
TRUST_POLICY_PATH="$SCRIPT_DIR/apprunner-ecr-access-trust-policy.json"
IMAGE_URI="$ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY:$IMAGE_TAG"
SERVICE_ARN=""
ACCESS_ROLE_ARN=""

require_command() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "required command not found: $1" >&2
    exit 1
  }
}

require_command aws
require_command docker
require_command python3

ensure_ecr_repository() {
  if ! aws ecr describe-repositories --region "$AWS_REGION" --repository-names "$ECR_REPOSITORY" >/dev/null 2>&1; then
    aws ecr create-repository --region "$AWS_REGION" --repository-name "$ECR_REPOSITORY" >/dev/null
  fi
}

ensure_access_role() {
  local existing_arn
  existing_arn="$(aws iam get-role --role-name "$APP_RUNNER_ACCESS_ROLE_NAME" --query 'Role.Arn' --output text 2>/dev/null || true)"

  if [ -n "$existing_arn" ] && [ "$existing_arn" != "None" ]; then
    ACCESS_ROLE_ARN="$existing_arn"
    return
  fi

  ACCESS_ROLE_ARN="$(aws iam create-role \
    --role-name "$APP_RUNNER_ACCESS_ROLE_NAME" \
    --assume-role-policy-document "file://$TRUST_POLICY_PATH" \
    --query 'Role.Arn' --output text)"

  aws iam attach-role-policy \
    --role-name "$APP_RUNNER_ACCESS_ROLE_NAME" \
    --policy-arn arn:aws:iam::aws:policy/service-role/AWSAppRunnerServicePolicyForECRAccess >/dev/null

  sleep 10
}

login_ecr() {
  aws ecr get-login-password --region "$AWS_REGION" \
    | docker login --username AWS --password-stdin "$ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com"
}

build_and_push_image() {
  docker build --platform "$DOCKER_PLATFORM" -t "$ECR_REPOSITORY:$IMAGE_TAG" "$BACKEND_DIR"
  docker tag "$ECR_REPOSITORY:$IMAGE_TAG" "$IMAGE_URI"
  docker push "$IMAGE_URI"
}

write_apprunner_payload() {
  python3 - <<PY
import json
import os
from pathlib import Path

payload = {
    "ServiceName": os.environ["APP_RUNNER_SERVICE_NAME"],
    "SourceConfiguration": {
        "AuthenticationConfiguration": {
            "AccessRoleArn": os.environ["ACCESS_ROLE_ARN"],
        },
        "AutoDeploymentsEnabled": os.environ["AUTO_DEPLOYMENTS_ENABLED"].lower() == "true",
        "ImageRepository": {
            "ImageIdentifier": os.environ["IMAGE_URI"],
            "ImageRepositoryType": "ECR",
            "ImageConfiguration": {
                "Port": os.environ["PORT"],
                "RuntimeEnvironmentVariables": {
                    "PORT": os.environ["PORT"],
                    "RUN_MIGRATIONS_ON_STARTUP": os.environ["RUN_MIGRATIONS_ON_STARTUP"],
                },
            },
        },
    },
    "InstanceConfiguration": {
        "Cpu": os.environ["CPU"],
        "Memory": os.environ["MEMORY"],
    },
}

optional_env = {
    "APP_ENV": os.getenv("APP_ENV"),
    "DATABASE_URL": os.getenv("DATABASE_URL"),
    "SECRET_KEY": os.getenv("SECRET_KEY"),
    "ACCESS_TOKEN_EXPIRE_MINUTES": os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"),
    "CORS_ORIGINS": os.getenv("CORS_ORIGINS"),
}

runtime_env = payload["SourceConfiguration"]["ImageRepository"]["ImageConfiguration"]["RuntimeEnvironmentVariables"]
for key, value in optional_env.items():
    if value:
        runtime_env[key] = value

Path(os.environ["PAYLOAD_PATH"]).write_text(json.dumps(payload, indent=2))
PY
}

find_existing_service() {
  aws apprunner list-services \
    --region "$AWS_REGION" \
    --query "ServiceSummaryList[?ServiceName=='$APP_RUNNER_SERVICE_NAME'].ServiceArn | [0]" \
    --output text
}

create_service() {
  aws apprunner create-service \
    --region "$AWS_REGION" \
    --cli-input-json "file://$PAYLOAD_PATH"
}

update_service() {
  aws apprunner update-service \
    --region "$AWS_REGION" \
    --service-arn "$SERVICE_ARN" \
    --source-configuration "file://$SOURCE_CONFIG_PATH"
}

wait_for_service() {
  local status=""
  local attempts=0
  local max_attempts=60

  while [ "$attempts" -lt "$max_attempts" ]; do
    status="$(aws apprunner describe-service       --region "$AWS_REGION"       --service-arn "$SERVICE_ARN"       --query 'Service.Status'       --output text)"

    case "$status" in
      RUNNING)
        return 0
        ;;
      CREATE_FAILED|UPDATE_FAILED|DELETE_FAILED|PAUSED|OPERATION_FAILED)
        echo "App Runner service entered unexpected status: $status" >&2
        return 1
        ;;
    esac

    attempts=$((attempts + 1))
    sleep 10
  done

  echo "Timed out while waiting for App Runner service. Last status: ${status:-unknown}" >&2
  return 1
}

PAYLOAD_PATH="$BACKEND_DIR/.apprunner-create.json"
SOURCE_CONFIG_PATH="$BACKEND_DIR/.apprunner-source-config.json"

ensure_ecr_repository
ensure_access_role
login_ecr
build_and_push_image

export AWS_REGION ACCOUNT_ID ECR_REPOSITORY APP_RUNNER_SERVICE_NAME IMAGE_TAG PORT RUN_MIGRATIONS_ON_STARTUP AUTO_DEPLOYMENTS_ENABLED CPU MEMORY DOCKER_PLATFORM IMAGE_URI PAYLOAD_PATH ACCESS_ROLE_ARN
export APP_ENV DATABASE_URL SECRET_KEY ACCESS_TOKEN_EXPIRE_MINUTES CORS_ORIGINS
write_apprunner_payload

python3 - <<PY
import json
from pathlib import Path
payload = json.loads(Path("$PAYLOAD_PATH").read_text())
Path("$SOURCE_CONFIG_PATH").write_text(json.dumps(payload["SourceConfiguration"], indent=2))
PY

SERVICE_ARN="$(find_existing_service)"
if [ -z "$SERVICE_ARN" ] || [ "$SERVICE_ARN" = "None" ]; then
  SERVICE_ARN="$(create_service | python3 -c 'import json,sys; print(json.load(sys.stdin)["Service"]["ServiceArn"])')"
else
  update_service >/dev/null
fi

wait_for_service
aws apprunner describe-service --region "$AWS_REGION" --service-arn "$SERVICE_ARN" \
  --query 'Service.{ServiceName:ServiceName,Status:Status,ServiceUrl:ServiceUrl}' --output table
