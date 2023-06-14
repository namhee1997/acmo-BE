docker-compose -f docker-compose.yml up splash

Activate environment
source envname/bin/activate

Deactivate
Command: deactivate

Install package
pip3 install package_name
Frezee Requirements
pip3 freeze > requirements.txt

Install requirements.txt
1: source envname/bin/activate
2: pip3 install -r requirements.txt

Run test
Command: py test -x Or Command: py test -x path_file

# add new package with pipenv
```
pipenv install package_name --skip-lock
```

## Important note:
Remember to export new package to requirements.txt. We will use requirements.txt to run in the docker.

# Copy env file
```
cp .env-staging .env
```
## Note 
- Edit the mongodb config and CORS
## Setup
### Vitual environment
```
python -m venv .venv
source .venv/bin/activate
```

### Freeze package
```
pip freeze -l > requirements.txt 
```
### Install lock packages
```
pip install -r requirements.txt
```
### Install package
```
pip install <package_name>
```
# Run dev
```
sh start-dev.sh
```

# if use folder migrations
alembic init migrations

# alembic.init file
script_location = migrations
# migration -> alembic init alembic

alembic init alembic

# create table

alembic revision --autogenerate -m "create table"

alembic upgrade head

