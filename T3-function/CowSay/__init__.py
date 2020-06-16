import logging
import json
import os
import pyodbc
import azure.functions as func


QUERY = 'SELECT TOP 1 author, quote FROM quotes ORDER BY newid()'

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    # connection_string = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=<server>.database.windows.net;PORT=1433;DATABASE=<database>;UID=<user>;PWD=<password>'
    connection_string = os.environ['CONNECTION_STRING']

    try:
        conn = pyodbc.connect(connection_string, timeout=3)

        cur = conn.cursor()
        author, quote = cur.execute(QUERY).fetchone()

        cur.close()
        conn.close()
    except pyodbc.OperationalError:
        author, quote = '503 Service Unavailable', 'Včera jsme měli párty a pili jsme těžko...'

    resp = {"author": author, "quote": quote}

    return func.HttpResponse(
        json.dumps(resp),
        headers={"Content-type": "application/json"},
        status_code=200
    )
