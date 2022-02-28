from curses import curs_set
import psycopg2

class DBHandler:
    def __init__(self, database, uname, pw, host="localhost"):
        self.database = database
        self.uname = uname
        self.pw = pw
        self.host = host
        self.connection = psycopg2.connect(
                host=self.host,
                database=self.database,
                user=self.uname,
                password=self.pw
            )
        self.cursor = self.connection.cursor()
    
    def executeQuery(self, query):
        self.cursor.execute(query)
        return self.cursor.fetchall()
    
    def reconnect(self):
        self.connection = psycopg2.connect(
                host=self.host,
                database=self.database,
                user=self.uname,
                password=self.pw
            )
        self.cursor = self.connection.cursor()