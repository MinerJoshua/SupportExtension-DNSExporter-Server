import mysql.connector
from mysql.connector import Error
import time
from config import DB_CONFIG

def get_connection():
    return mysql.connector.connect(**DB_CONFIG)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id VARCHAR(64) PRIMARY KEY,
            status ENUM('starting','parsing package list','fetching DNS data and writing to Zone file', 'completed','failed') NOT NULL DEFAULT 'starting',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            input_data TEXT,
            result_path TEXT,
            error TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS failed_job_items (
            job_id VARCHAR(64),
            package_id INT,
            zone_path TEXT,
            error TEXT,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            PRIMARY KEY (job_id, package_id)
        )
    """)

    conn.commit()
    cursor.close()
    conn.close()


def update_job_status(job_id, status, result_path=None, error=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE jobs
        SET status = %s, result_path = %s, error = %s
        WHERE id = %s
    """, (status, result_path, error, job_id))
    conn.commit()
    cursor.close()
    conn.close()

def save_job(job_id, input_data, status="starting"):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO jobs (id, status, input_data)
        VALUES (%s, %s, %s)
    """, (job_id, status, json.dumps(input_data)))
    conn.commit()
    cursor.close()
    conn.close()

def update_failed_job_item(job_id ,package_id, zone_path):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO failed_job_items (job_id, package_id, zone_path)
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE,
            zone_path = VALUES(zone_path),
            updated_at = CURRENT_TIMESTAMP
    """, (job_id, package_id, zone_path))
    conn.commit()
    cursor.close()
    conn.close()

def cancel_job(job_id, reason):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE jobs
        SET status = %s, error = %s
        WHERE id = %s
    """, ("failed", reason, job_id))
    conn.commit()
    cursor.close()
    conn.close()