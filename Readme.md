Installlation steps:
1. Install PostgreSQL
2. Change .env.dist to .env, and fill required fields in .env
3. Install all required dependencies: 
``` 
pip install -r requirements.txt
```
4. Create migrations with: 
``` 
alembic revision -m "your migration description" --autogenerate --head head
```
5. Migrate tables with Alembic:
```
alembic upgrade head
```
6. To start bot execute "bot.py" in root directory 