
## Run with Docker (preferred for production)

create an `stack.env` file in root directory with key "TOKEN" and a value of the bots token.

`docker-compose up --build -d`

`docker-compose up -d`

## Stop Docker

`docker-compose down`

## Run without docker (when developing)

create an `.env` file in root directory with key "TOKEN" and a value of the bots token.

run `uv run python main.py`