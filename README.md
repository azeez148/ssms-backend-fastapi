# SSMS Backend (FastAPI)

This is the FastAPI version of the SSMS (Shop Stock Management System) backend.

## Setup

1. Make sure you have Python 3.7+ installed

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure PostgreSQL:
   - Install PostgreSQL if not already installed
   - Set the following environment variables (or use defaults):
     ```
     POSTGRES_USER=postgres
     POSTGRES_PASSWORD=postgres
     POSTGRES_SERVER=localhost
     POSTGRES_PORT=5432
     POSTGRES_DB=ssms_db
     ```

4. Apply database migrations:
```bash
alembic upgrade head
```

5. Import initial category data (after running migrations):
```bash
# For Windows (Option 1) - Using full path to psql:
"C:\Program Files\PostgreSQL\{version}\bin\psql.exe" -U postgres -d ssms_db -f category_data.sql

# For Windows (Option 2) - Using pgAdmin Query Tool:
- Open pgAdmin
- Connect to your database
- Right-click on 'ssms' database
- Select 'Query Tool'
- Click the folder icon (Open File)
- Navigate to and select 'category_data.sql'
- Click the Execute button (or F5)

# For Linux/Mac
psql -h localhost -U postgres -d ssms -f category_data.sql
```

Note: For Windows Option 1, replace {version} with your PostgreSQL version number (e.g., 14, 15, 16).
If you don't know your PostgreSQL version or installation path:
1. Open pgAdmin
2. Right-click on your server
3. Select "Properties"
4. Look for "Version" in the Properties window

6. Run the development server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## Database Migrations

This project uses Alembic to manage database migrations.

To create a new migration script after making changes to the SQLAlchemy models:
```bash
alembic revision --autogenerate -m "A descriptive message about the changes"
```

Then, apply the migrations to the database:
```bash
alembic upgrade head
```

## API Documentation

Once the server is running, you can access:
- Interactive API documentation (Swagger UI): http://localhost:8000/docs
- Alternative API documentation (ReDoc): http://localhost:8000/redoc

## Project Structure

```
app/
├── api/            # API endpoints
├── core/           # Core functionality (database, config)
├── models/         # SQLAlchemy models
├── schemas/        # Pydantic schemas
├── services/       # Business logic
└── main.py        # Application entry point
```

## Features

- Product management
- Category management
- Stock management
- Sales tracking
- Purchase tracking
- Shop management
- Payment types
- Delivery types
- Dashboard statistics
- Image upload support

## Notifications

This application can send email notifications when a sale is completed. To enable this feature, you need to configure the following environment variables:

### Email (SMTP)

- `MAIL_USERNAME`: Your SMTP username.
- `MAIL_PASSWORD`: Your SMTP password.
- `MAIL_FROM`: The email address to send notifications from.
- `MAIL_PORT`: The port of your SMTP server.
- `MAIL_SERVER`: The hostname or IP address of your SMTP server.
- `MAIL_TLS`: Set to `True` to use TLS.
- `MAIL_SSL`: Set to `True` to use SSL.
