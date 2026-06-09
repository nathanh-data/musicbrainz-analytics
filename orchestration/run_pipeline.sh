#!/bin/bash

PROJECT_DIR="/c/musicbrainz-analytics"

cd "$PROJECT_DIR"

LOG_DIR=logs

mkdir -p $LOG_DIR

LOG_FILE=$LOG_DIR/pipeline_$(date +%Y%m%d_%H%M%S).log

{
echo "================================="
echo "Début pipeline : $(date)"
echo "================================="

./venv/Scripts/python.exe scripts/extraction/api_musicbrainz.py || exit 1

psql \
-d musicbrainz_db \
-U postgres \
-f sql/materialized_views/refresh_views.sql

echo "================================="
echo "Fin pipeline : $(date)"
echo "================================="
} >> $LOG_FILE 2>&1