# fastapi-example

Usual operation:
```bash
make build
docker compose up --detach
docker compose exec postgres psql -U appuser -d appdb
docker compose logs -f fastapi-example
docker compose down
```
