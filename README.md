## LangChain Query over SQL Database

### Overview

This project demonstrates the use of LangChain to build an SQL query chain using a Large Language Model (LLM) from OpenAI. The script performs several key tasks, including querying a MySQL database, utilizing few-shot learning to improve the quality of generated SQL queries, and employing custom prompts and tools to dynamically execute SQL queries and return human-readable results.

### Requirements

To use this project, you need to have the following dependencies installed:

- **Python 3.8+**
- **LangChain** and associated libraries for LLM and prompt handling
- **MySQL Database** with credentials stored in an `.env` file
- **OpenAI API Key** (also stored in the `.env` file)

Install the necessary Python packages using:

```bash
pip install langchain mysqlclient python-dotenv pymysql
```

### Environment Setup

This project relies on environment variables to securely manage sensitive information, such as the database connection parameters and the OpenAI API key. You must create a `.env` file in the root directory with the following details:

```
DB_USER=<your_database_user>
DB_PASSWORD=<your_database_password>
DB_HOST=<your_database_host>
DB_NAME=<your_database_name>
OPENAI_API_KEY=<your_openai_api_key>
OPENAI_MODEL=<openai_model_name>  # Example: gpt-3.5-turbo
OPENAI_API_HOST=<openai_api_host>
```

### Key Components

1. **Database Connection Setup**:
   The script connects to a MySQL database using the `SQLDatabase` class from LangChain's community tools. This connection is established using the credentials stored in the `.env` file.

   ```python
   db = SQLDatabase.from_uri(f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}")
   ```

2. **LLM Integration**:
   The script integrates the OpenAI LLM via the `ChatOpenAI` class, configured with the `OPENAI_API_KEY`. This LLM is used to generate SQL queries based on input prompts and return results in natural language.

   ```python
   llm = ChatOpenAI(temperature=0, model=os.environ.get('OPENAI_MODEL'), api_key=os.environ.get('OPENAI_API_KEY'), base_url=os.environ.get('OPENAI_API_HOST'))
   ```

3. **Few-Shot Learning**:
   Few-shot examples are used to guide the LLM to generate more accurate SQL queries. These examples are stored in the `few_shot_examples.py` module.

   ```python
   few_shot_prompt = order_few_shot
   ```

4. **Custom Prompt Templates**:
   Custom prompt templates are created using `ChatPromptTemplate` to ensure that the LLM produces a correct MySQL query and interprets the results correctly. The prompt also includes error-handling rules to improve the accuracy of generated queries.

   ```python
   custom_prompt = ChatPromptTemplate.from_messages([...])
   ```

5. **SQL Query Chain**:
   The SQL query chain is built using LangChain's `create_sql_query_chain` method, which pipes together components for generating SQL queries, executing them, and returning the results.

   ```python
   sql_chain = create_sql_query_chain(llm, db, custom_prompt)
   ```

6. **Query Execution**:
   SQL queries are executed using the `QuerySQLDataBaseTool`, which runs the SQL query on the connected MySQL database and returns the results.

   ```python
   execute_query = QuerySQLDataBaseTool(db=db)
   ```

7. **Final Chain Execution**:
   The final result chain runs the query generation, SQL execution, and response generation in sequence. This chain uses LangChain's `RunnableLambda` to execute the query and return the parsed result.

   ```python
   rephrased_chain = (
       RunnablePassthrough.assign(sql_query=clean_sql_chain)
       .assign(sql_result=itemgetter("sql_query") | execute_query)
       | rephrased_answer_chain
   )
   ```

### Example Usage

The script executes the following example query:

```python
{
    "question": "List of Employees with the concern customers",
    "table_info": table_info,
    "top_k": few_shot_prompt
}
```

The chain generates an appropriate SQL query based on the `table_info` and returns the result in human-readable format.

### How to Run

1. Ensure you have configured the `.env` file with valid database credentials and OpenAI API details.
2. Install the required dependencies as mentioned in the **Requirements** section.
3. Run the script using Python:

   ```bash
   python main.py
   ```

4. The script will print the result of the query in a human-readable format.

### Resources

This project follows an example from LangChain's SQL Query Quickstart. You can find more information about the implementation of SQL queries in LangChain [here](https://python.langchain.com/v0.1/docs/use_cases/sql/quickstart).

### Notes

- Ensure that the database schema is correct and matches the table information provided in the prompts.
- Be careful with queries that involve sensitive or large datasets; always validate generated SQL queries before executing them on production data.

### Troubleshooting

- **Database Connection Errors**: Ensure that the `.env` file is correctly configured with the MySQL credentials.
- **LLM Errors**: If the LLM is not generating correct SQL queries, review the few-shot examples and custom prompt template for accuracy.
