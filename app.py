import os
import sys
from urllib import parse
from datetime import datetime, timedelta

import dotenv
import pymysql.cursors
from bottle import default_app, route, run, template,request, abort, HTTPResponse

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')

dotenv.load_dotenv(dotenv_path)
os.environ.get('')

JAWSDB_URL = os.environ.get('JAWSDB_URL')
url = parse.urlparse(JAWSDB_URL)
db_info = {
	'NAME': url.path[1:],
	'USER': url.username,
	'PASSWORD': url.password,
	'HOST': url.hostname,
	'PORT': url.port if url.port else 3306,
}

@route("/")
def hello_world():
  return "hello server"

@route("/server", method=['GET'])
def get_list():
    con = pymysql.connect(user=db_info.get('USER'),
                          passwd=db_info.get('PASSWORD'),
                          host=db_info.get('HOST'),
                          db=db_info.get('NAME'))
    cur = con.cursor()
    sql = "select * from server"
    cur.execute(sql)
    rows = cur.fetchall()
    cur.close
    con.close
    servers = []
    for row in rows:
        one = {}
        one.update({
            'id': row[0],
            'hostname': row[1],
            'ip': row[2],
            'update_time': row[3]
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
    con = pymysql.connect(user=db_info.get('USER'),
                          passwd=db_info.get('PASSWORD'),
                          host=db_info.get('HOST'),
                          db=db_info.get('NAME'))
    cur = con.cursor()
    sql = "insert into server (hostname, ip_address, updated_time) values ('{0}', '{1}', '{2}')  on duplicate key update hostname='{0}', ip_address='{1}';".format(data["hostname"], data["eth0_ip"], (datetime.now() + timedelta(hours=9)).strftime('%Y-%m-%d %H:%M:%S'))
    print(sql)
    cur.execute(sql)
    con.commit()
    cur.close
    con.close
    return HTTPResponse(status=200, body="OK")
  else:
    return abort(code=400, text="Bad data")



if __name__ == '__main__':
    # run(host="gunicorn")
    run(port=8000)  # for localhost
app = default_app()