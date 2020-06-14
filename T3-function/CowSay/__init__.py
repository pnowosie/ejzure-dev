import logging
import json
import os
import pyodbc
import azure.functions as func


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    # connection_string = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=<server>.database.windows.net;PORT=1433;DATABASE=<database>;UID=<user>;PWD=<password>'
    connection_string = os.environ['CONNECTION_STRING']
    
    conn = pyodbc.connect(connection_string)

    cur = conn.cursor()
    cur.execute('SELECT TOP 1 author, quote FROM quotes ORDER BY newid();')
    author, quote = cur.fetchone()

    resp = {"author": author, "quote": quote}
    cur.close()
    conn.close()

    return func.HttpResponse(
        json.dumps(resp),
        headers={"Content-type": "application/json"},
        status_code=200
    )
