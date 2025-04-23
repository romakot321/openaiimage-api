#!/bin/bash
cd lib/python3.13/site-packages/app/db && alembic -c alembic.prod.ini upgrade head && cd /app
proxychains4 gunicorn app.main:fastapi_app -w 1 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:80 --forwarded-allow-ips="*"
