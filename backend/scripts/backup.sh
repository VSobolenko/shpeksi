#!/bin/sh
# MongoDB backup loop for the Pickup backend.
#
# Runs inside the compose `backup` service (official mongo image, which ships
# mongodump/mongorestore). Dumps the `pickup` database to a gzipped archive on
# a schedule and keeps the most recent BACKUP_KEEP archives.
#
# Restore (from the host, or a shell in the `backup` container):
#   mongorestore --host mongo --port 27017 --username "$MONGO_INITDB_ROOT_USERNAME" \
#     --password "$MONGO_INITDB_ROOT_PASSWORD" --authenticationDatabase admin \
#     --drop --gzip --archive=/backups/pickup_<timestamp>.archive
set -eu

HOST="${MONGO_HOST:-mongo}"
PORT="${MONGO_PORT:-27017}"
USER="${MONGO_INITDB_ROOT_USERNAME:-pickup}"
PASS="${MONGO_INITDB_ROOT_PASSWORD:-change-me}"
DB="${MONGODB_DB_NAME:-pickup}"
BACKUP_DIR="${BACKUP_DIR:-/backups}"
INTERVAL="${BACKUP_INTERVAL_SECONDS:-86400}"
KEEP="${BACKUP_KEEP:-14}"

mkdir -p "${BACKUP_DIR}"

while true; do
  STAMP="$(date +%Y%m%d_%H%M%S)"
  OUT="${BACKUP_DIR}/${DB}_${STAMP}.archive"

  mongodump \
    --host "${HOST}" --port "${PORT}" \
    --username "${USER}" --password "${PASS}" \
    --authenticationDatabase admin \
    --db "${DB}" \
    --archive="${OUT}" \
    --gzip

  echo "backup written to ${OUT}"

  # Prune older archives, keeping the newest KEEP files.
  find "${BACKUP_DIR}" -name "${DB}_*.archive" -type f \
    | sort -r \
    | tail -n +"$((KEEP + 1))" \
    | xargs -r rm -f

  sleep "${INTERVAL}"
done
