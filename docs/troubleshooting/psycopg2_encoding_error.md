# psycopg2 encoding error on Windows

## Error
'utf-8' codec can't decode byte 0xe9...

## Root cause
PostgreSQL using WIN1252 encoding due to Windows locale.

## Attempts
- client_encoding UTF8 ❌
- PGCLIENTENCODING ❌
- psycopg2-binary ❌

## Solution
Switch to psycopg3:

pip install "psycopg[binary]"

## Result
Connection successful.