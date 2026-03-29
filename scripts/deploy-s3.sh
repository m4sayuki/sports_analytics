#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BUCKET="${1:-${S3_BUCKET:-}}"
REGION="${AWS_REGION:-ap-northeast-1}"
PREFIX="${S3_PREFIX:-}"
HTML_CACHE_CONTROL="${HTML_CACHE_CONTROL:-no-cache, no-store, must-revalidate}"
ASSET_CACHE_CONTROL="${ASSET_CACHE_CONTROL:-no-cache, must-revalidate}"

if [[ -z "$BUCKET" ]]; then
  echo "S3 bucket is required. Pass it as the first argument or set S3_BUCKET." >&2
  exit 1
fi

TARGET="s3://${BUCKET}"
if [[ -n "$PREFIX" ]]; then
  CLEAN_PREFIX="${PREFIX#/}"
  CLEAN_PREFIX="${CLEAN_PREFIX%/}"
  TARGET="${TARGET}/${CLEAN_PREFIX}"
fi

echo "Uploading static files to ${TARGET} (${REGION})"

aws s3 cp "${ROOT_DIR}/index.html" "${TARGET}/index.html"   --region "$REGION"   --content-type "text/html; charset=utf-8"   --cache-control "$HTML_CACHE_CONTROL"

aws s3 cp "${ROOT_DIR}/styles.css" "${TARGET}/styles.css"   --region "$REGION"   --content-type "text/css; charset=utf-8"   --cache-control "$ASSET_CACHE_CONTROL"

aws s3 cp "${ROOT_DIR}/app.js" "${TARGET}/app.js"   --region "$REGION"   --content-type "application/javascript; charset=utf-8"   --cache-control "$ASSET_CACHE_CONTROL"

echo "Upload complete."
