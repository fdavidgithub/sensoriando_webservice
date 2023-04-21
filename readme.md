# Sensoriando
**Hub de Sensores**
[web.sensoriando.com.br](http://web.sensoriando.com.br)

## Requirement
Homologated
* Ubuntu 18.04

```console
sudo apt-get update
sudo apt-get upgrade
```

### Python
```console
sudo apt-get install python3-pip
```

### Postgres
```console
sudo apt-get install postgresql-13 postgresql-client-13
```


## Install

2. Django init
```console
source ~/envs/Sensoriando/bin/activate
pytnon manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

3. Django runtime
```console
python manage.py runserver
```

4. Browser URL
localhost:8000

## Run
### Virtualenv
echo "127.0.0.1 sensoriando_database" >> /etc/hosts
source venv/bin/activate

### via Docker local
```console
docker-compose up
```

Executar o comando **docker-compose build** novamente para reconstruir a imagem do serviço sempre que o arquivo requiriment.txt ou Dockerfile for alterado


### Docker shared
```console
docker-compose -f docker-compose-shared up
```
When use docker-compose-shared, need create .env file

```
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=sensoriando
```

### Prompt database
#### Docker
docker exec -it sensoriando_database psql -U postgres -d sensoriando
#### Native
psql -U postgres -d sensoriando

### Shell
docker exec -it sensoriando_webservice-django-1 python manage.py [command]
