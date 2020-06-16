import logging
import json
import os
import pyodbc
import azure.functions as func


QUERY = 'INSERT INTO quotes(author, quote) VALUES (?, ?)'

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Add new quote to database')
    # connection_string = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=<server>.database.windows.net;PORT=1433;DATABASE=<database>;UID=<user>;PWD=<password>'
    connection_string = os.environ['CONNECTION_STRING']

    status_code = 200
    author, quote = None, None
    try:
        body = req.get_json()
        author = body.get('author')
        quote = body.get('quote')
    except ValueError:
        status_code = 400

    try:    
        conn = pyodbc.connect(connection_string, timeout=3, autocommit=True)

        cur = conn.cursor()
        count = cur.execute(QUERY, (author, quote)).rowcount
        if count == 1:
            status_code = 201  

        cur.close()
    except pyodbc.OperationalError:
        status_code = 503
    except pyodbc.DatabaseError:
        status_code = 400
        conn.rollback()
    finally:
        conn and conn.close()

    return func.HttpResponse(None, status_code=status_code)
