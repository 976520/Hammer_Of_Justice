import mysql.connector
from mysql.connector import Error
import os
import asyncio
import logging
from functools import partial

logger = logging.getLogger(__name__)

DB_HOST = os.getenv('DB_HOST')
DB_PORT = int(os.getenv('DB_PORT', '3306'))
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')
DB_CHARSET = 'utf8mb4'

async def get_connection():
    try:
        loop = asyncio.get_event_loop()
        connection = await loop.run_in_executor(
            None,
            partial(
                mysql.connector.connect,
                host=DB_HOST,
                port=DB_PORT,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME
            )
        )
        logger.info(f"get_connection OKAY: {DB_HOST}:{DB_PORT}")
        return connection
    except Error as e:
        logger.error(f"get_connection ERROR: {e}")
        return None

async def create_tables():
    connection = await get_connection()
    if connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS counts (
                    user_id VARCHAR(20),
                    server_id VARCHAR(20),
                    count INT NOT NULL DEFAULT 0,
                    PRIMARY KEY (user_id, server_id)
                )
                ''')
            connection.commit()
            logger.info("create_tables OKAY")
        except Exception as e:
            logger.error(f"create_tables ERROR: {e}")
        finally:
            connection.close()
    else:
        logger.error("데이터베이스 연결 실패")

async def get_user_count(user_id, server_id):
    connection = await get_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            sql = "SELECT count FROM counts WHERE user_id = %s AND server_id = %s"
            cursor.execute(sql, (user_id, server_id))
            result = cursor.fetchone()
            cursor.close()
            if result:
                return result['count']
            return 0
        except Exception as e:
            logger.error(f"get_user_count ERROR: {e}")
            return 0
        finally:
            connection.close()
    return 0

async def update_user_count(user_id, server_id, count):
    connection = await get_connection()
    if connection:
        try:
            with connection.cursor() as cursor:
                sql = """
                INSERT INTO counts (user_id, server_id, count) 
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE count = %s
                """
                cursor.execute(sql, (user_id, server_id, count, count))
            connection.commit()
            logger.info(f"update_user_count OKAY: {user_id} - {count}")
            return True
        except Exception as e:
            logger.error(f"update_user_count ERROR: {e}")
        finally:
            connection.close()
    return False 