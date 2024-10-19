from sqlalchemy import create_engine, inspect
import os
from os.path import join, dirname
from dotenv import load_dotenv

from langchain_community.utilities.sql_database import SQLDatabase
from prettytable import PrettyTable
from sqlalchemy import text
import pandas as pd

# Loading the environment variables
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

# Initialize the SQLAlchemy engine (replace with your database URI)
engine = create_engine(f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}")


# Step 1: Define the find_relevant_group method
table_groups = {
    "Customer Order": ["customers", "orders", "orderdetails"],
    "Order Details": ["orders", "orderdetails", "products", "productlines"],
    "Sales Detailed Report": ["customers", "employees", "orders", "orderdetails", "products", "productlines"]
}

def find_relevant_group(question):
    if "Customer" in question:
        return table_groups["Customer Order"]
    elif "Product" in question or "Order" in question:
        return table_groups["Order Details"]
    else:
        return table_groups["Sales Detailed Report"]

def get_table_ddl(table):
    with engine.connect() as connection:
        query = text(f'SHOW CREATE TABLE {table};')
        result = connection.execute(query).fetchone()
        ddl = result[1]  # type: ignore # The CREATE TABLE statement is in the second column
    return ddl


# Step 2: Define the get_table_info method (fetch schema)
def get_table_info(tables_to_inspect):
    """
    Fetches schema information for the tables provided in the 'tables_to_inspect' list.
    """
    schema_info = {}

    # Fetch table creation SQL
    for table in tables_to_inspect:
        ddl = get_table_ddl(table)
        schema_info[table] = ddl
    
    return schema_info


# Step 3: Define the get_sample_data method (fetch sample data)
def get_sample_data(table_name, limit=3):
    """
    Fetch sample data for the given table.
    """
    with engine.connect() as connection:
        query = text(f'SELECT * FROM {table_name} LIMIT {limit};')
        result = connection.execute(query)
        rows = result.fetchall()
        
        # Extract column headers
        headers = result.keys()
        return rows, headers

# Step 4: Function to retrieve table descriptions from a CSV file
def get_table_details():
    """
    Reads the table descriptions from a CSV file and returns a dictionary where
    the key is the table name and the value is the table description.
    """
    # Read the CSV file into a DataFrame
    table_description = pd.read_csv("database_table_descriptions.csv")
    
    # Create a dictionary to store table descriptions
    table_docs = {}
    
    # Iterate over the DataFrame rows to create table descriptions
    for index, row in table_description.iterrows():
        table_docs[row['Table']] = row['Description']

    return table_docs

# Step 5: Function to format the output including schema, descriptions, and sample data
def format_output(schema_info, sample_data, table_descriptions):
    """
    Format the schema, sample data, and table descriptions in the desired format.
    """
    output = ""
    
    for table, ddl in schema_info.items():
        # Add the table description if available
        if table in table_descriptions:
            output += f"Table Name: {table}\n{table_descriptions[table]}\n\n"
        
        # Add the DDL directly without manually prepending 'CREATE TABLE {table}'
        output += f"{ddl}\n"
        
        if table in sample_data:
            rows, headers = sample_data[table]
            
            # Use PrettyTable to format the table output
            table_output = PrettyTable()
            table_output.field_names = headers
            
            for row in rows:
                table_output.add_row(row)
            
            output += f"\n/*\n{len(rows)} rows from {table} table:\n{table_output}\n*/\n"
    
    return output


# Combine the steps and generate the response
def process_query(question):
    # Step 1: Find the relevant table group based on the user's question
    relevant_tables = find_relevant_group(question)
    
    # Step 2: Fetch the table schema for relevant tables
    schema_details = get_table_info(relevant_tables)
    
    # Step 3: Fetch sample data for the relevant tables
    sample_data = {}
    for table in relevant_tables:
        data, headers = get_sample_data(table)
        sample_data[table] = (data, headers)
        
    # Step 4: Fetch the table descriptions from the CSV file
    table_descriptions = get_table_details()

    # Step 5: Format the output as per the required format
    formatted_output = format_output(schema_details, sample_data, table_descriptions)
    return formatted_output

# Example usage
# output = process_query("Sales")

# Print the formatted result
# print(output)
