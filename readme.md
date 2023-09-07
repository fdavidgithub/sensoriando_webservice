# Sensoriando
**Hub de Sensores**
[web.sensoriando.com.br](http://web.sensoriando.com.br)

## Install

1. Create docker's images
```console
docker-compose build
```

2. Docker
```console
docker-compose up -d
```

3. Environment
Create .env file

```console
touch .env
```
```console
export POSTGRES_HOST=sensoriando_database
export POSTGRES_USER=postgres
export POSTGRES_PASSWORD=[your password]
export POSTGRES_DB=sensoriando
export POSTGRES_PORT=5432
```

5. Reload
```console
docker-compose restart
```

