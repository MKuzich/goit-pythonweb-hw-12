# goit-pythonweb-hw-12

python -m venv venv
pip install -r requirements.txt

postgresql://postgres:pass@db:5432/postgres
docker run --name postgres -p 5432:5432 -e POSTGRES_PASSWORD=pass -d postgres
docker run -d -p 6379:6379 redis

docker-compose up --build
