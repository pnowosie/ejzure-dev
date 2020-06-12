import logging
import json
import os
import psycopg2
import azure.functions as func


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    # connection_dsn = 'user=DB_USER@AZURE_DB_SERVER password=xxx dbname=DB_NAME host=AZURE_DB_SERVER.postgres.database.azure.com port=5432'
    connection_dsn = os.environ['CONNECTION_STRING']
    
    conn = psycopg2.connect(connection_dsn)

    cur = conn.cursor()
    cur.execute('SELECT author, quote FROM quotes ORDER BY random();')
    author, quote = cur.fetchone()

    resp = {"author": author, "quote": quote}
    cur.close()
    conn.close()

    return func.HttpResponse(
        json.dumps(resp),
        headers={"Content-type": "application/json"},
        status_code=200
    )
