import re
import os
from os.path import join, dirname
from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect


# Loading the environment variables
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

def get_table_info(tables_to_inspect):
    """
    Fetches schema information for the tables provided in the 'tables_to_inspect' list.
    """
    # Database connection parameters
    engine = create_engine(f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}")
    inspector = inspect(engine)
    schema_info = {}
    
    # Only get schema details for tables in the provided list
    for table in tables_to_inspect:
        if table in inspector.get_table_names():
            columns = inspector.get_columns(table)
            schema_info[table] = [{"name": col["name"], "type": str(col["type"])} for col in columns]
        else:
            print(f"Table {table} not found in the database.")
    
    return schema_info

# Extract SQL query from the response
def extract_sql_query(response: str) -> str:
    # Regular expression to extract SQL query
    match = re.search(r"(SELECT.*?;)", response, re.DOTALL)
    if match:
        return match.group(1)
    else:
        raise ValueError("No valid SQL query found in the response.")
    
# Helper function to ensure environment variables are correctly set
def get_env_variable(var_name, default=None):
    value = os.environ.get(var_name, default)
    if value is None:
        raise ValueError(f"Environment variable {var_name} is not set.")
    return value