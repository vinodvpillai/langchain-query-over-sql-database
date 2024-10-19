import os
from os.path import join, dirname
from dotenv import load_dotenv

from langchain_community.utilities.sql_database import SQLDatabase

# Loading the environment variables
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

# Database connection parameters
db = SQLDatabase.from_uri(f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}")
print(db.dialect)
print(db.get_usable_table_names())
print(db.table_info)

print(db.run("SELECT * FROM customers LIMIT 10;"))



