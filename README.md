
## Run with Docker (preferred for production)

create an `stack.env` file in root directory with key "TOKEN" and a value of the bots token.

`docker-compose up --build -d`

`docker-compose up -d`

## Stop Docker

`docker-compose down`

## Run without docker (when developing)

create an `.env` file in root directory with key "TOKEN" and a value of the bots token.

run `uv run python main.py`

start database:
`brew services start mongodb-community@8.0`

Invite bot:
https://discord.com/oauth2/authorize?client_id=1364339419259338762&permissions=274877908992&integration_type=0&scope=bot