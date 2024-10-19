import os
from os.path import join, dirname
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
#from langchain_community.chat_models import ChatOpenAI
from langchain_community.utilities.sql_database import SQLDatabase
from langchain.chains import create_sql_query_chain
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from langchain_core.runnables import RunnableLambda
from util import extract_sql_query


# Loading the environment variables
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

# Database connection parameters
db = SQLDatabase.from_uri(f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}")

# LLM Model
llm = ChatOpenAI(temperature=0, model=os.environ.get('OPENAI_MODEL'), api_key=os.environ.get('OPENAI_API_KEY'), base_url=os.environ.get('OPENAI_API_HOST')) # type: ignore

# Query Chain
sql_chain = create_sql_query_chain(llm, db)
clean_sql_chain = sql_chain | RunnableLambda(lambda x: x.replace('```', '').replace('sql', ''))

# Query - This will return the SQL Query
clean_response = clean_sql_chain.invoke({"question":"How many employees are there?"})

# Extract only the SQL query
try:
    sql_query = extract_sql_query(clean_response)
    print(f"Extracted SQL Query: {sql_query}")
    
    # Run the extracted SQL query
    result = db.run(sql_query)
    print(result)
except ValueError as e:
    print(f"Error: {e}")


