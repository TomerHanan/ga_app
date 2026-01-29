"""
FastAPI application that connects to PostgreSQL database.
Configured to run in Kubernetes with environment variables.
"""

import os
import psycopg2
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Initialize FastAPI app
app = FastAPI(title="GA App", version="1.0.0")

# Database configuration from environment variables
DB_NAME = os.getenv("POSTGRES_DB", "postgres")
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "password")
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")


def get_db_connection():
    """Create and return a PostgreSQL database connection."""
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        host=DB_HOST,
        port=DB_PORT
    )


class Record(BaseModel):
    """Request model for creating a log record."""
    message: str


@app.on_event("startup")
def setup_db():
    """Initialize database table on application startup."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS logs (
                id SERIAL PRIMARY KEY, 
                message TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()
        cur.close()
        conn.close()
        print("Database initialized successfully")
    except Exception as e:
        print(f"Error initializing database: {e}")


@app.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "up", "message": "Application is running"}


@app.post("/write")
def write_to_db(record: Record):
    """Write a message to the PostgreSQL database."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO logs (message) VALUES (%s) RETURNING id, created_at;",
            (record.message,)
        )
        result = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        
        return {
            "status": "success",
            "id": result[0],
            "message": record.message,
            "created_at": str(result[1])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/logs")
def get_logs(limit: int = 10):
    """Retrieve the latest log messages from the database."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT id, message, created_at FROM logs ORDER BY created_at DESC LIMIT %s;",
            (limit,)
        )
        logs = cur.fetchall()
        cur.close()
        conn.close()
        
        return {
            "status": "success",
            "count": len(logs),
            "logs": [
                {
                    "id": log[0],
                    "message": log[1],
                    "created_at": str(log[2])
                }
                for log in logs
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/logs/{log_id}")
def get_log(log_id: int):
    """Retrieve a specific log message by ID."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT id, message, created_at FROM logs WHERE id = %s;",
            (log_id,)
        )
        log = cur.fetchone()
        cur.close()
        conn.close()
        
        if not log:
            raise HTTPException(status_code=404, detail="Log not found")
        
        return {
            "status": "success",
            "id": log[0],
            "message": log[1],
            "created_at": str(log[2])
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
