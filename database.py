import psycopg2
import psycopg2.extras
from psycopg2.pool import SimpleConnectionPool
import os
from dotenv import load_dotenv

load_dotenv()

class Database:
    def __init__(self):
        self.pool = None
        self.init_pool()
    
    def init_pool(self):
        """Initialize connection pool"""
        try:
            self.pool = SimpleConnectionPool(
                1, 20,  # min and max connections
                host=os.getenv('DB_HOST', 'localhost'),
                database=os.getenv('DB_NAME', 'attendance_db'),
                user=os.getenv('DB_USER', 'postgres'),
                password=os.getenv('DB_PASSWORD', 'password'),
                port=os.getenv('DB_PORT', '5432')
            )
            print("Database connection pool created successfully")
        except Exception as e:
            print(f"Error creating connection pool: {e}")
            raise
    
    def get_connection(self):
        """Get connection from pool"""
        return self.pool.getconn()
    
    def return_connection(self, conn):
        """Return connection to pool"""
        self.pool.putconn(conn)
    
    def execute_query(self, query, params=None, fetch=False):
        """Execute a query and return results if needed"""
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute(query, params)
            
            if fetch:
                result = cursor.fetchall()
                return result
            else:
                conn.commit()
                return cursor.rowcount
        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if conn:
                cursor.close()
                self.return_connection(conn)
    
    def execute_one(self, query, params=None):
        """Execute query and return one result"""
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute(query, params)
            result = cursor.fetchone()
            return result
        except Exception as e:
            raise e
        finally:
            if conn:
                cursor.close()
                self.return_connection(conn)

# Global database instance
db = Database()