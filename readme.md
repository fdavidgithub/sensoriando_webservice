# Sensoriando
**Hub de Sensores**

## [Business Plan](doc/businessplan.md)

## [Requirement](doc/requirement.md)

## [Setup](doc/setup.md)

## Install

1. Create database
```console
./install.sh
```

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



