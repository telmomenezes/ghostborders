import MySQLdb
import _mysql_exceptions


class DB:
    def __init__(self, dbname, config):
        self.dbname = dbname
        self.host = config.data['db']['host']
        self.user = config.data['db']['user']
        self.password = config.data['db']['password']
        self.conn = None
        self.cur = None

    def open(self):
        self.conn = MySQLdb.connect(host=self.host, user=self.user, passwd=self.password, db=self.dbname)
        self.cur = self.conn.cursor()

    def close(self):
        self.cur.close()
        self.conn.close()

    def query(self, q):
        self.cur = self.conn.cursor()
        self.cur.execute(q)
        res = self.cur.fetchall()
        self.cur.close()
        return res

    def __exec_or_ignore(self, query):
        print('Executing query: %s' % query)
        try:
            self.cur.execute(query)
            print('executed.')
        except _mysql_exceptions.OperationalError:
            print('ignored.')
        except _mysql_exceptions.ProgrammingError:
            print('ignored.')

    def create_db(self):
        # create database
        self.conn = MySQLdb.connect(host="localhost", user="root", passwd="")
        self.cur = self.conn.cursor()

        self.__exec_or_ignore("CREATE DATABASE %s" % self.dbname)

        self.conn.commit()
        self.close()

        # create tables
        self.open()

        # create media table
        self.__exec_or_ignore("CREATE TABLE media (id BIGINT PRIMARY KEY)")
        self.__exec_or_ignore("ALTER TABLE media MODIFY id BIGINT AUTO_INCREMENT")
        self.__exec_or_ignore("ALTER TABLE media AUTO_INCREMENT = 1000000")
        self.__exec_or_ignore("ALTER TABLE media ADD COLUMN user BIGINT")
        self.__exec_or_ignore("ALTER TABLE media ADD COLUMN location BIGINT")
        self.__exec_or_ignore("ALTER TABLE media ADD COLUMN ts BIGINT")
        self.__exec_or_ignore("ALTER TABLE media ADD COLUMN lat DOUBLE")
        self.__exec_or_ignore("ALTER TABLE media ADD COLUMN lng DOUBLE")
        self.__exec_or_ignore("ALTER TABLE media ADD COLUMN ig_id VARCHAR(255)")
        self.__exec_or_ignore("ALTER TABLE media ADD COLUMN distance DOUBLE DEFAULT -1")

        self.__exec_or_ignore("CREATE UNIQUE INDEX unique_media_ig_id ON media(ig_id)")
        self.__exec_or_ignore("CREATE INDEX media_ig_id ON media (ig_id)")
        self.__exec_or_ignore("CREATE INDEX media_user ON media (user)")
        self.__exec_or_ignore("CREATE INDEX media_ts ON media (ts)")

        # create user table
        self.__exec_or_ignore("CREATE TABLE user (id BIGINT PRIMARY KEY)")
        # self.__exec_or_ignore("ALTER TABLE user MODIFY id BIGINT AUTO_INCREMENT")
        # self.__exec_or_ignore("ALTER TABLE user AUTO_INCREMENT = 1000000")
        self.__exec_or_ignore("ALTER TABLE user ADD COLUMN username VARCHAR(255)")
        self.__exec_or_ignore("ALTER TABLE user ADD COLUMN homelat DOUBLE")
        self.__exec_or_ignore("ALTER TABLE user ADD COLUMN homelng DOUBLE")
        self.__exec_or_ignore("ALTER TABLE user ADD COLUMN home BIGINT")
        self.__exec_or_ignore("ALTER TABLE user ADD COLUMN first_ts BIGINT DEFAULT -1")
        self.__exec_or_ignore("ALTER TABLE user ADD COLUMN last_ts BIGINT DEFAULT -1")
        self.__exec_or_ignore("ALTER TABLE user ADD COLUMN photos BIGINT DEFAULT 0")

        self.__exec_or_ignore("CREATE INDEX user_username ON user (username)")

        # create locations table
        self.__exec_or_ignore("CREATE TABLE location (id BIGINT PRIMARY KEY)")
        self.__exec_or_ignore("ALTER TABLE location MODIFY id BIGINT AUTO_INCREMENT")
        self.__exec_or_ignore("ALTER TABLE location AUTO_INCREMENT = 1000000")
        self.__exec_or_ignore("ALTER TABLE location ADD COLUMN country VARCHAR(255)")
        self.__exec_or_ignore("ALTER TABLE location ADD COLUMN name VARCHAR(255)")
        self.__exec_or_ignore("ALTER TABLE location ADD COLUMN lat DOUBLE")
        self.__exec_or_ignore("ALTER TABLE location ADD COLUMN lng DOUBLE")
        self.__exec_or_ignore("ALTER TABLE location ADD COLUMN min_ts BIGINT DEFAULT -1")
        self.__exec_or_ignore("ALTER TABLE location ADD COLUMN done BIGINT")
        
        # create likes table
        self.__exec_or_ignore("CREATE TABLE likes (id BIGINT PRIMARY KEY)")
        self.__exec_or_ignore("ALTER TABLE likes MODIFY id BIGINT AUTO_INCREMENT")
        self.__exec_or_ignore("ALTER TABLE likes AUTO_INCREMENT = 1000000")
        self.__exec_or_ignore("ALTER TABLE likes ADD COLUMN user BIGINT")
        self.__exec_or_ignore("ALTER TABLE likes ADD COLUMN media BIGINT")
        self.__exec_or_ignore("ALTER TABLE likes ADD COLUMN location BIGINT")
        self.__exec_or_ignore("ALTER TABLE likes ADD COLUMN ts BIGINT")

        self.__exec_or_ignore("CREATE INDEX likes_user_media ON likes (user, media)")
        self.__exec_or_ignore("CREATE INDEX likes_user ON likes (user)")
        self.__exec_or_ignore("CREATE INDEX likes_ts ON likes (ts)")

        # create comment table
        self.__exec_or_ignore("CREATE TABLE comment (id BIGINT PRIMARY KEY)")
        self.__exec_or_ignore("ALTER TABLE comment MODIFY id BIGINT AUTO_INCREMENT")
        self.__exec_or_ignore("ALTER TABLE comment AUTO_INCREMENT = 1000000")
        self.__exec_or_ignore("ALTER TABLE comment ADD COLUMN user BIGINT")
        self.__exec_or_ignore("ALTER TABLE comment ADD COLUMN media BIGINT")
        self.__exec_or_ignore("ALTER TABLE comment ADD COLUMN location BIGINT")
        self.__exec_or_ignore("ALTER TABLE comment ADD COLUMN ts BIGINT")
        self.__exec_or_ignore("ALTER TABLE comment ADD COLUMN distance DOUBLE DEFAULT -1")

        self.__exec_or_ignore("CREATE INDEX comment_user_media ON comment (user, media)")
        self.__exec_or_ignore("CREATE INDEX comment_user ON comment (user)")
        self.__exec_or_ignore("CREATE INDEX comment_ts ON comment (ts)")

        # create table userlocation
        self.__exec_or_ignore("CREATE TABLE userlocation (user BIGINT)")
        self.__exec_or_ignore("ALTER TABLE userlocation ADD COLUMN location BIGINT")
        self.__exec_or_ignore("ALTER TABLE userlocation ADD COLUMN weight BIGINT")
        self.__exec_or_ignore("ALTER TABLE userlocation ADD COLUMN w DOUBLE")
        self.__exec_or_ignore("CREATE INDEX userlocation_user ON userlocation (user)")
        self.__exec_or_ignore("CREATE INDEX userlocation_location ON userlocation (location)")

        # create table locationlocation
        self.__exec_or_ignore("CREATE TABLE locationlocation (loc1 BIGINT)")
        self.__exec_or_ignore("ALTER TABLE locationlocation ADD COLUMN loc2 BIGINT")
        self.__exec_or_ignore("ALTER TABLE locationlocation ADD COLUMN weight BIGINT")
        self.__exec_or_ignore("ALTER TABLE locationlocation ADD COLUMN month CHAR(7) DEFAULT NULL")

        # create table month
        self.__exec_or_ignore("CREATE TABLE month (id CHAR(7))")
        self.__exec_or_ignore("ALTER TABLE month ADD COLUMN first_seen_users BIGINT")
        self.__exec_or_ignore("ALTER TABLE month ADD COLUMN last_seen_users BIGINT")
        self.__exec_or_ignore("ALTER TABLE month ADD COLUMN photos BIGINT")

        self.conn.commit()
