# Luma - Flashcard App Backend

This repository contains the backend API for the Luma flashcard application. It is built with Python using the FastAPI framework and provides all the necessary endpoints to power the mobile app's features, including user authentication, deck management, and study session tracking.

## Tech Stack 🛠️

* **Framework**: FastAPI
* **Database**: PostgreSQL
* **ORM**: SQLAlchemy
* **Data Validation**: Pydantic
* **Password Hashing**: Passlib with Bcrypt
* **Server**: Uvicorn
* **Dependency Management**: Pip with `requirements.txt`
* **Environment Variables**: python-dotenv
* **Database (local development)**: Docker

---
## Project Structure

The project follows a scalable, feature-based structure to separate concerns.

```
/luma-backend/
├── /app/                   # Main application folder
│   ├── __init__.py
│   ├── main.py             # Main FastAPI app instance
│   ├── database.py         # Database session setup
│   ├── models.py           # SQLAlchemy models
│   ├── schemas.py          # Pydantic schemas
│   ├── crud.py             # Database logic (Create, Read, Update, Delete)
│   └── routers/            # Folder for API endpoints (routers)
│       ├── __init__.py
│       └── users.py
│       └── decks.py
│
├── .env                    # Local environment variables (ignored by Git)
├── .env.example            # Example environment variables
├── .gitignore
├── README.md
└── requirements.txt        # Python dependencies
```

---
## Setup and Installation 🚀

Follow these steps to get the development environment running locally.

### 1. Prerequisites

* Python 3.10+
* Docker Desktop (running)

### 2. Clone the Repository

```bash
git clone <your-repository-url>
cd luma-backend
```

### 3. Create a Virtual Environment

```bash
# For macOS/Linux
python -m venv venv
source venv/bin/activate

# For Windows
python -m venv venv
.\venv\Scripts\activate
```

### 4. Install Dependencies

Install all the required Python packages from the `requirements.txt` file.

```bash
pip install -r requirements.txt
```
> **Note:** If you haven't created a `requirements.txt` file yet, you can generate it with this command: `pip freeze > requirements.txt`


### 5. Start the PostgreSQL Database

Run the following Docker command to start a PostgreSQL container. This will create a database named `luma_db` with a user and password.

```bash
docker run --name luma-postgres -e POSTGRES_USER=myuser -e POSTGRES_PASSWORD=mypassword -e POSTGRES_DB=luma_db -p 5432:5432 -d postgres:15
```

### 6. Configure Environment Variables

Create a `.env` file for your local database credentials. You can copy the example file to start.

```bash
# For macOS/Linux
cp .env.example .env

# For Windows
copy .env.example .env
```
Now, open the newly created `.env` file and make sure the `DATABASE_URL` matches the credentials used in the Docker command.

```env
# .env
DATABASE_URL="postgresql://myuser:mypassword@localhost:5432/luma_db"
```

---
## Running the Application

With the virtual environment activated and the database running, start the FastAPI server using Uvicorn.

```bash
uvicorn app.main:app --reload
```
The API will be available at `http://127.0.0.1:8000`.

---
## API Endpoints

This API provides endpoints for managing Users, Decks, Words, and more.

For a complete, interactive list of all available endpoints and to test them directly from your browser, visit the auto-generated Swagger UI documentation after running the application:

**[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)**