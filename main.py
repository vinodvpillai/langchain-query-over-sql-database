import os
from os.path import join, dirname
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_community.utilities.sql_database import SQLDatabase
from langchain.chains import create_sql_query_chain
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
# Part 2 - Passing the result & question to LLM with prompt
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from operator import itemgetter
from langchain_core.runnables import RunnableLambda
from util import extract_sql_query
# Part 3 - Few shot learning
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, FewShotChatMessagePromptTemplate
from few_shot_examples import order_few_shot
# Part 4 - Custom Prompt 
from custom_prompt_table_info import process_query


# Loading the environment variables
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

# Database connection parameters
db = SQLDatabase.from_uri(f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}")

# LLM Model
llm = ChatOpenAI(temperature=0, model=os.environ.get('OPENAI_MODEL'), api_key=os.environ.get('OPENAI_API_KEY'), base_url=os.environ.get('OPENAI_API_HOST'))  # type: ignore

# ------------------- Table Info + Few Shot Example -------------------
# Table info
table_info = process_query("Sales")

# Few Shot Learning
few_shot_prompt = order_few_shot

# Final Prompt
custom_prompt = ChatPromptTemplate.from_messages(
     [
         ("system", """You are a MySQL expert. Given an input question, first create a syntactically correct MySQL query to run, then look at the results of the query and return the answer to the input question. \n\nHere is the relevant table info: {table_info}\n\n

         \n\nBelow are a number of examples of questions and their corresponding SQL queries.
         {top_k} \n\n

         Generate a syntactically correct MySQL query based on the information provided.
            Important Rules:
            Double check the generate query for common mistakes, including:
            - Using NOT IN with NULL values
            - Using UNION when UNION ALL should have been used
            - Using BETWEEN for exclusive ranges
            - Data type mismatch in predicates
            - Properly quoting identifiers
            - Using the correct number of arguments for functions
            - Casting to the correct data type
            - Using the proper columns for joins

        If there are any of the above mistakes, rewrite the query.
        If there are no mistakes, just reproduce the original query with no further commentary.
          """),
         ("human", "{input}"),
     ]
 )
# ------------------- End => Few Shot + Dynamic selector + Custom Prompt -------------------

# Query Chain
sql_chain = create_sql_query_chain(llm, db, custom_prompt) 
clean_sql_chain = sql_chain | RunnableLambda(lambda x: extract_sql_query(x)) # type: ignore

# Execute Query - This will execute the SQL Query and give result
execute_query = QuerySQLDataBaseTool(db=db)

# Custom Prompt
answer_prompt = PromptTemplate.from_template(
    """Given the following user question, corresponding SQL query, and SQL result, answer the user question.\n\n
    Important Rules:
    - Never query for all columns from a table. You must query only the columns that are needed to answer the question. Wrap each column name in double quotes (") to denote them as delimited identifiers.
    - Pay attention to use only the column names you can see in the tables below. Be careful to not query for columns that do not exist. Also, pay attention to which column is in which table.
    - Pay attention to use date('now') function to get the current date, if the question involves 'today'.
    
    User Question: {question}
    SQL Query: {sql_query}
    SQL Result: {sql_result}
    Answer:
    """
)

# Chain
rephrased_answer_chain = answer_prompt | llm | StrOutputParser()

rephrased_chain = (
    RunnablePassthrough.assign(sql_query=clean_sql_chain).assign(
        sql_result=itemgetter("sql_query") | execute_query
        )
        | rephrased_answer_chain 
    )


# Calling the LLM with the final prompt
print(rephrased_chain.invoke({
    "question": "List of Employees with the concern customers", 
    "table_info": table_info, 
    "top_k": few_shot_prompt
}))

# "question": "Total number of orders?", 