temporal order workflow

# local env:

```
source venv/bin/activate
```

# docker:

```
docker compose up
```

# if sql permission errors:

### run docker in detached mode

### exec into sql and give root permission

```
docker compose up -d

docker exec -it temporal_order_workflow-mysql-1 mysql -u root -ptemporal

CREATE DATABASE IF NOT EXISTS temporal;
CREATE DATABASE IF NOT EXISTS temporal_visibility;

CREATE USER IF NOT EXISTS 'temporal'@'%' IDENTIFIED BY 'temporal';
GRANT ALL PRIVILEGES ON temporal._ TO 'temporal'@'%';
GRANT ALL PRIVILEGES ON temporal_visibility._ TO 'temporal'@'%';
FLUSH PRIVILEGES;
EXIT;

docker compose restart temporal
```

# start temporal

```
uvicorn src.api.server:app --reload
```

# exit:

```
docker compose down
deactivate
```

# test

```
curl http://localhost:7233
```

# start temporal

```
uvicorn src.api.server:app --reload
```

## postgres (not using)

## inside docker -psql:

```
docker exec -it temporal_order_workflow-postgres-1 psql -U ${POSTGRES_USER} -d ${POSTGRES_DB}
psql -h localhost -p 5432 -U [PWD] -d [DB]
```
