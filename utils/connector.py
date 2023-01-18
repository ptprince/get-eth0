import logging
import os
import ssl
import sys
from datetime import datetime, timedelta
from urllib.parse import urlparse

import pg8000.dbapi
import pymysql.cursors

logger = logging.getLogger()
for h in logger.handlers:
    logger.removeHandler(h)

h = logging.StreamHandler(sys.stdout)

FORMAT = '%(levelname)s %(asctime)s [%(filename)s:%(lineno)d] [%(funcName)s] %(message)s'
h.setFormatter(logging.Formatter(FORMAT))
logger.addHandler(h)

logger.setLevel(logging.INFO)

sslContext = ssl.create_default_context()
sslContext.check_hostname = False
sslContext.verify_mode = ssl.CERT_NONE

class dbConnector:
    def __init__(self, db_url: str) -> None:
        logger.info('Started database connection')
        self.db_info = self.parse_mysql_url(db_url)
        try:
            if self.db_info.scheme == 'postgres':
                pass
                self.sql_conn = pg8000.dbapi.connect(
                    host=self.db_info.hostname,
                    port=self.db_info.port if 'port' in self.db_info else '5432',
                    user=self.db_info.username,
                    password=self.db_info.password,
                    database=self.db_info.path[1:],
                    ssl_context=sslContext
                    )
            else:
                self.sql_conn = pymysql.connect(
                    init_command='SET SESSION time_zone="+09:00"',
                    host=self.db_info.hostname,
                    port=self.db_info.port if 'port' in self.db_info else '3306',
                    user=self.db_info.username,
                    passwd=self.db_info.password,
                    database=self.db_info.path[1:],
                    connect_timeout=10,  # 変更可
                    cursorclass=pymysql.cursors.DictCursor  # sqlのレスポンスがdictがいいなら指定
                )

            self.cur = self.sql_conn.cursor()

        except Exception as e:
            logger.error('Start mysql connection failed')
            logger.error(e)

    def __del__(self):
        try:
            self.sql_conn.close()
            logger.info('Mysql connection closed')
        except Exception as e:
            logger.error('Close Mysql connection failed')
            logger.error(e)

    def fetch(self, sql, count=None):
        try:
            self.cur.execute(sql)
            sql_res = dict()
            if count is None:
                sql_res = self.cur.fetchall()
            else:
                sql_res = self.cur.fetchmany(count)
            return sql_res
        except Exception as e:
            logger.error(F'Fetch sql for [{sql}] failed')
            logger.debug(e)
            return None

    def execute_many(self, sql, data):
        try:
            self.cur.executemany(sql, data)
            return True
        except Exception as e:
            logger.error(F'Execute sql for [{sql}] failed')
            logger.debug(e)
            self.sql_conn.rollback()
            return False

    def delete_rows(self, sql):
        try:
            sql_res = self.cur.execute(sql)
            logger.debug(sql_res)
            return sql_res
        except Exception as e:
            logger.error(F'Execute sql for [{sql}] failed')
            logger.debug(e)
            self.sql_conn.rollback()
            return None


    def commit(self):
        try:
            self.sql_conn.commit()
            return True
        except Exception as e:
            logger.error(F'Do DB commit failed {e}')
            return False

    def get_line_token(self, campsite_id):
        logger.info(F'Start getting line token for {campsite_id}')
        try:
            select_line_token_sql = F'SELECT line_notify_token,deleted_at FROM app_contact_information WHERE campsite_id = {campsite_id}'
            self.cur.execute(select_line_token_sql)
            line_notify_token_item = self.cur.fetchone()
            if line_notify_token_item['deleted_at'] != None:
                logger.error(F'Line token for {campsite_id} is invalid')
                return None
            return line_notify_token_item['line_notify_token']
        except:
            logger.error(F'Get line token for {campsite_id} failed')
            return None

    def get_reserve_id(self, rsv_dtl_list_id):
        logger.info(F'Start getting rsv_id for {rsv_dtl_list_id}')
        try:
            select_rsv_id_sql = F'SELECT rl.rsv_id FROM rsv_dtl_list rdl INNER JOIN rsv_list rl ON rdl.rsv_list_id = rl.rsv_list_id WHERE rdl.rsv_dtl_list_id = "{rsv_dtl_list_id}"'
            self.cur.execute(select_rsv_id_sql)
            rsv_id = self.cur.fetchone()
            return rsv_id['rsv_id']
        except:
            logger.info(F'Get rsv_id for {rsv_dtl_list_id} failed')
            return None

    def parse_mysql_url(self, url: str):
        try:
            db_info = urlparse(url)
            logger.debug('Parsed db info:')
            logger.debug({db_info})
            return db_info
        except:
            return


if __name__ == '__main__':
    sql_url = 'mysql://nap_ntt:wWei8^9x@localhost:13306/nap_db_1'
    campsite_id = 10000
    rsv_dtl_list_id = 6860992
    my_connection = dbConnector(sql_url)
    camp_info = my_connection.get_line_token(campsite_id)
    print(camp_info)
    rsv_id = my_connection.get_reserve_id(rsv_dtl_list_id)
    print(rsv_id)
