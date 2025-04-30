# fastapi-example

Usual operation:
```bash
docker compose up --detach --build
docker compose exec postgres psql -U appuser -d appdb
docker compose logs -f app
docker compose down
```
