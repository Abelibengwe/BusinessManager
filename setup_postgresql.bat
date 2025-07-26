@echo off
echo Setting up Business Manager with PostgreSQL...
echo.

echo 1. Installing Python dependencies...
pipenv install

echo.
echo 2. Installing additional dependencies...
pipenv install psycopg2-binary python-decouple

echo.
echo PostgreSQL Database Setup Complete!
echo.
echo Next steps:
echo 1. Install PostgreSQL from https://www.postgresql.org/download/windows/
echo 2. Create database and user (see POSTGRESQL_SETUP.md for details)
echo 3. Copy .env.example to .env and update with your database credentials
echo 4. Run: python manage.py makemigrations
echo 5. Run: python manage.py migrate
echo 6. Run: python manage.py createsuperuser
echo 7. Run: python manage.py runserver
echo.
pause
