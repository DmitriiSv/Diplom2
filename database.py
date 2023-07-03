import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

class Database:
    def __init__(self, dbname, user, password, host, port):
        self.dbname = os.getenv('db_name')
        self.user = os.getenv('user')
        self.password = os.getenv('password')
        self.host = os.getenv('host')
        self.port = os.getenv('port')
        self.conn = None
         
    def connect(self):
        self.conn = psycopg2.connect(
            dbname=self.dbname,
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port
        )

    def create_table(self):
        self.connect()
        cur = self.conn.cursor()
        cur.execute('CREATE TABLE IF NOT EXISTS usersvk (id serial PRIMARY KEY, vk_id integer UNIQUE, '
                    'vk_url varchar);')
        self.conn.commit()
        cur.close()
         

    def save_usersvk(self, vk_id, vk_url):
        self.connect()
        cur = self.conn.cursor()
        cur.execute('INSERT INTO usersvk (vk_id, vk_url) VALUES (%s, %s);', (vk_id, vk_url))
        self.conn.commit()
        cur.close()
         

    def check_usersvk(self, vk_id):
        self.connect()
        cur = self.conn.cursor()
        cur.execute('SELECT vk_id FROM usersvk WHERE vk_id = %s;', (vk_id,))
        result = cur.fetchone()
        cur.close()
        if result:
            return True

    def delete_table(self):
        self.connect()
        cur = self.conn.cursor()
        cur.execute('DROP TABLE IF EXISTS usersvk;')
        self.conn.commit()
        cur.close()
         

    def disconnect(self):
        self.conn.close()
         