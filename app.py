import logging
import os
import sys
from datetime import datetime, timedelta, timezone
from urllib import parse

import dotenv

from bottle import (HTTPResponse, abort, default_app, request, route, run,
                    template)

from utils.connector import dbConnector

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')

dotenv.load_dotenv(dotenv_path)


logger = logging.getLogger()
for h in logger.handlers:
    logger.removeHandler(h)

h = logging.StreamHandler(sys.stdout)

FORMAT = '%(levelname)s %(asctime)s [%(filename)s:%(lineno)d] [%(funcName)s] %(message)s'
h.setFormatter(logging.Formatter(FORMAT))
logger.addHandler(h)

logger.setLevel(os.environ.get('LOG_LEVEL')if os.environ.get('LOG_LEVEL') else logging.INFO)

JST = timezone(timedelta(hours=+9), 'JST')

DB_URL = os.environ.get('DB_URL')


@route("/")
def hello_world():
  return "hello server"

@route("/server", method=['GET'])
def get_list():
  con = dbConnector(DB_URL)
  sql = "select * from server"
  rows = con.fetch(sql)
  servers = []
  if  rows != None and len(rows)> 0:
    logger.info(rows)
    for row in rows:
        one = {}
        one.update({
            'id': row.get('id'),
            'hostname': row.get('hostname'),
            'ip': row.get('ip_address'),
            'des': row.get('description'),
            'update_time': row.get('updated_time')
        })
        servers.append(one)
  return template('./views/index.html', servers=servers)  # ここで返す内容は何でもよい

@route("/server", method=['POST'])
def save_ip():
  contentType = request.get_header('Content-Type')
  if contentType != "application/json":
    return abort(code=400, text="Bad content type")
  data = request.json
  if ("hostname" in data.keys()) and ("eth0_ip" in data.keys()):
    con = dbConnector(DB_URL)
    if con.db_info.scheme == 'postgres':
      sql = "insert into server (hostname, ip_address, updated_time) values ('{0}', '{1}', '{2}')  ON CONFLICT (hostname) DO UPDATE SET hostname='{0}', ip_address='{1}', updated_time='{2}';".format(data["hostname"], data["eth0_ip"], (datetime.now(JST)).strftime('%Y-%m-%d %H:%M:%S'))
    else:
      sql = "insert into server (hostname, ip_address, updated_time) values ('{0}', '{1}', '{2}')  on duplicate key update hostname='{0}', ip_address='{1}', updated_time='{2}';".format(data["hostname"], data["eth0_ip"], (datetime.now(JST)).strftime('%Y-%m-%d %H:%M:%S'))
    print(sql)
    con.cur.execute(sql)
    con.commit()
    return HTTPResponse(status=200, body="OK")
  else:
    return abort(code=400, text="Bad data")



if __name__ == '__main__':
    # run(host="gunicorn")
    run(port=8000)  # for localhost
app = default_app()