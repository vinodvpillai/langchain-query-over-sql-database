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

# Loading the environment variables
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

# Database connection parameters
db = SQLDatabase.from_uri(f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}")

# LLM Model
llm = ChatOpenAI(temperature=0, model=os.environ.get('OPENAI_MODEL'), api_key=os.environ.get('OPENAI_API_KEY'), base_url=os.environ.get('OPENAI_API_HOST'))  # type: ignore

# Query Chain
sql_chain = create_sql_query_chain(llm, db)
clean_sql_chain = sql_chain | RunnableLambda(lambda x: extract_sql_query(x)) # type: ignore

# Execute Query - This will execute the SQL Query and give result
execute_query = QuerySQLDataBaseTool(db=db)

# Custom Prompt
answer_prompt = PromptTemplate.from_template(
    """Given the following user question, corresponding SQL query, and SQL result, answer the user question.
    
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

# Few Shot Learning
example_prompt = ChatPromptTemplate.from_messages(
     [
         ("human", "{input}\nSQLQuery:"),
         ("ai", "{query}"),
     ]
 )

few_shot_prompt = FewShotChatMessagePromptTemplate(
     example_prompt=example_prompt,
     examples=order_few_shot,
     input_variables=["input"]
 )

print(few_shot_prompt.format(user_query="How many products are there?"))