import pyodbc

try:
    # SQLALCHEMY_DATABASE_URI = ("DRIVER={SQL Server};SERVER=DESKTOP-TRPSBPE\SQLEXPRESS;DATABASE=OCRDB_dev;")
    SQLALCHEMY_DATABASE_URI = ("DRIVER={SQLite3 ODBC Driver};SERVER=localhost;DATABASE=OCRDB_dev.db;Trusted_connection=yes")
    connection = pyodbc.connect(SQLALCHEMY_DATABASE_URI)
    print("SQL Server connection successful!")
    connection.close()
except Exception as e:
    print(f"Connection failed: {e}")