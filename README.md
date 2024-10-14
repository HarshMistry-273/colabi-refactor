# Colabi Project

This README provides instructions for setting up and running a FastAPI project using Python 3.12.0, including virtual environment creation, dependency installation, running the server and Celery workers, and managing database migrations with Alembic.

## Prerequisites

- Python 3.12.0
- pip (Python package installer)
- Docker (for Redis)

## Setting up the Environment

### 1. Create a Virtual Environment

```bash
python -m venv venv
```

### 2. Activate the Virtual Environment

#### On Windows:
```bash
venv\Scripts\activate
```

#### On macOS and Linux:
```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## Database Management with Alembic

### Initialize Alembic (if not already initialized)

```bash
alembic init alembic
```

### Create a New Migration

```bash
alembic revision --autogenerate -m "Description of the change"
```

### Apply Migrations

To upgrade the database to the latest version:

```bash
alembic upgrade head
```

To upgrade or downgrade to a specific version:

```bash
alembic upgrade <revision>
alembic downgrade <revision>
```

### View Migration History

```bash
alembic history --verbose
```

## Running the Application

### Start the FastAPI Server

To run the FastAPI server:

```bash
python main.py
```

The `reload=True` flag enables hot reloading during development. Remove this flag for production deployment from `main.py`.

### Start Celery Workers

#### On Windows:
```bash
celery -A src.celery worker --pool=solo -l info
```

#### On macOS and Linux:
```bash
celery -A src.celery worker -l info
```

## Running Redis with Docker

To run Redis using Docker, use the following command:

```bash
docker run -d -p 6379:6379 redis:latest
```

This command will pull the latest Redis image if it's not already available locally and run it in detached mode, mapping port 6379 on your host to port 6379 in the container.

## Project Structure

```
.
├── main.py
├── alembic/
│   ├── versions/
│   └── env.py
├── alembic.ini
├── database/
├── src/
│   ├── __init__.py
│   ├── celery.py
│   ├── app.py
│   ├── config.py
│   ├── preprocessing.py
│   ├── agents/
│   ├── crew_agents/
│   ├── tasks/
│   ├── tools/
│   └── utils/
├── .env
├── requirements.txt
└── README.md
```

## Additional Notes

- Ensure that all required environment variables are set before running the application.
- Always keep your `requirements.txt` file up to date when adding or removing dependencies.
- FastAPI provides automatic API documentation. Once your server is running, you can access:
  - Swagger UI: `http://localhost:8000/docs`
  - ReDoc: `http://localhost:8000/redoc`
- When making changes to your database models, create and apply Alembic migrations to keep your database schema in sync with your code.

## Example `requirements.txt`

Here's a sample `requirements.txt` file for the Colabi project:

```
crewai==0.67.1
crewai-tools==0.12.1
langchain-google-community==1.0.8
langchain==0.2.16
langchain-community==0.2.17
python-dotenv==1.0.1
langchain-google-genai==1.0.10
fastapi==0.115.0
PyMySQL==1.1.1
langchain-pinecone==0.1.3
langchain-openai==0.1.25
celery==5.4.0
redis==5.1.1
alembic==1.12.0
SQLAlchemy==2.0.23
# Add any other project-specific dependencies here
```

Remember to adjust the versions according to your specific needs and to keep them updated.
