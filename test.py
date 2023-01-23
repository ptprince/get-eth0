import os
import ssl
import sys
from datetime import datetime, timedelta
from urllib import parse

import dotenv
import psycopg2
import pymysql.cursors
from bottle import (HTTPResponse, abort, default_app, request, route, run,
                    template)

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')

dotenv.load_dotenv(dotenv_path)

DB_URL = os.environ.get('DB_URL')
url = parse.urlparse(DB_URL)

db_info = {
	'NAME': url.path[1:],
	'USER': url.username,
	'PASSWORD': url.password,
	'HOST': url.hostname,
	'PORT': url.port,
  'type': url.scheme
}


con = pg8000.dbapi.connect(
      host=db_info.get('HOST'),
      port='5432',
      user=db_info.get('USER'),
      password=db_info.get('PASSWORD'),
      database=db_info.get('NAME'),
      ssl_context=True)

cur = con.cursor()

sql = "select * from server"
cur.execute(sql)
result = cur.fetchall()

create_table_sql = F'''
CREATE TABLE IF NOT EXISTS server (
    id SERIAL NOT NULL,
    hostname VARCHAR(255) NOT NULL UNIQUE,
    ip_address  VARCHAR(255) NOT NULL,
    description VARCHAR(255),
    updated_time    timestamp 
)
'''

delete_table_sql = F'''
DROP TABLE IF EXISTS server
'''

# result = cur.execute(create_table_sql)
print(result)
# con.commit()