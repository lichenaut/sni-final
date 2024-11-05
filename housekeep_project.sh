#!/bin/bash

# Please know that this script updates packages blindly and deletes backend/db.sqlite3.

rm -rf backend/db.sqlite3
. $(pwd)/venv/bin/activate
pip freeze > requirements.txt
pip install -r requirements.txt
cd backend && python3 manage.py makemigrations && python3 manage.py migrate && cd ..
black $(pwd)
deactivate

cd frontend && pnpm install && pnpm prettier --write . && cd ..
