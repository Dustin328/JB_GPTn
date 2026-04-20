"""
Database initialization script
Run this to create the MySQL database and tables
"""
import os
from dotenv import load_dotenv
import pymysql

# Load environment variables
load_dotenv()

DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = int(os.getenv('DB_PORT', 3306))
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_NAME = os.getenv('DB_NAME', 'jailbrokegpt')

def create_database():
    """Create the database if it doesn't exist"""
    print(f"Connecting to MySQL server at {DB_HOST}:{DB_PORT}...")
    
    try:
        # Connect without specifying database
        connection = pymysql.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD
        )
        
        cursor = connection.cursor()
        
        # Create database
        print(f"Creating database '{DB_NAME}'...")
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print(f"✓ Database '{DB_NAME}' created or already exists")
        
        cursor.close()
        connection.close()
        
        # Now create tables using SQLAlchemy
        print("\nCreating tables...")
        from models import init_db
        init_db()
        print("✓ All tables created successfully")
        
        print("\n" + "="*50)
        print("Database setup complete!")
        print("="*50)
        print("\nYou can now start the server with: python app.py")
        
    except pymysql.Error as e:
        print(f"\n❌ Error: {e}")
        print("\nPlease check:")
        print("1. MySQL server is running")
        print("2. Credentials in .env file are correct")
        print(f"3. User '{DB_USER}' has permission to create databases")
        return False
    
    return True

if __name__ == '__main__':
    print("="*50)
    print("JailbrokeGPT Database Setup")
    print("="*50)
    print(f"\nConfiguration:")
    print(f"  Host: {DB_HOST}:{DB_PORT}")
    print(f"  User: {DB_USER}")
    print(f"  Database: {DB_NAME}")
    print()
    
    create_database()
