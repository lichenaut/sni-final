#!/bin/bash

filter_numbers() {
    while read line; do
        if [[ "$line" =~ ^[0-9]+$ ]]; then
            echo "$line"
        fi
    done
}

cleanup() {
    kill $frontend_pid
    kill $backend_pid
    deactivate
    exit 0
}

trap cleanup SIGINT

. $(pwd)/venv/bin/activate
cd backend && python3 manage.py runserver &>> ../backend.log &
backend_pid=$(echo $! | filter_numbers)
cd frontend && pnpm dev -o &>> ../frontend.log &
frontend_pid=$(echo $! | filter_numbers)

echo "Starting servers! Visit http://localhost:8000/ and http://localhost:3000/ in-browser."
echo "Press CONTROL+C to quit."

while true; do
    sleep 10
done
