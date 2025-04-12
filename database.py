import mysql.connector
from mysql.connector import Error
import os

DB_HOST = os.getenv('DB_HOST')
DB_PORT = int(os.getenv('DB_PORT', '3306'))
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')
DB_CHARSET = 'utf8mb4'

def get_connection():
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        return connection
    except Error as e:
        print(e)
        return None

def create_tables():
    connection = get_connection()
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
            print("테이블 생성")
        except Exception as e:
            print(e)
        finally:
            connection.close()
    else:
        print("DB연결 실패")

def get_user_count(user_id, server_id):
    connection = get_connection()
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
            print(e)
            return 0
        finally:
            connection.close()
    return 0

def set_user_count(user_id, server_id, count):
    connection = get_connection()
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
            print('set: ', user_id, server_id, count)
            return True
        except Exception as e:
            print(e)
        finally:
            connection.close()
    return False 