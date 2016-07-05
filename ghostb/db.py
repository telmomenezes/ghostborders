#   Copyright (c) 2016 Centre Marc Bloch Berlin
#   (An-Institut der Humboldt Universität, UMIFRE CNRS-MAE).
#   All rights reserved.
#
#   Written by Telmo Menezes <telmo@telmomenezes.com>
#
#   This file is part of GhostBorders.
#
#   GhostBorders is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   GhostBorders is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with GhostBorders.  If not, see <http://www.gnu.org/licenses/>.


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

        self.__exec_or_ignore("CREATE UNIQUE INDEX unique_media_ig_id ON media(ig_id)")
        self.__exec_or_ignore("CREATE INDEX media_ig_id ON media (ig_id)")
        self.__exec_or_ignore("CREATE INDEX media_user ON media (user)")
        self.__exec_or_ignore("CREATE INDEX media_ts ON media (ts)")

        # create user table
        self.__exec_or_ignore("CREATE TABLE user (id BIGINT PRIMARY KEY)")
        self.__exec_or_ignore("ALTER TABLE user MODIFY id BIGINT AUTO_INCREMENT")
        self.__exec_or_ignore("ALTER TABLE user ADD COLUMN username VARCHAR(255)")
        self.__exec_or_ignore("ALTER TABLE user ADD COLUMN active BIGINT DEFAULT 0")
        self.__exec_or_ignore("ALTER TABLE user ADD COLUMN dists_str MEDIUMTEXT DEFAULT NULL")
        self.__exec_or_ignore("ALTER TABLE user ADD COLUMN mean_dist DOUBLE DEFAULT 0")
        self.__exec_or_ignore("ALTER TABLE user ADD COLUMN mean_weighted_dist DOUBLE DEFAULT 0")
        self.__exec_or_ignore("ALTER TABLE user ADD COLUMN mean_time_interval DOUBLE DEFAULT 0")
        self.__exec_or_ignore("ALTER TABLE user ADD COLUMN first_ts BIGINT DEFAULT -1")
        self.__exec_or_ignore("ALTER TABLE user ADD COLUMN last_ts BIGINT DEFAULT -1")
        self.__exec_or_ignore("ALTER TABLE user ADD COLUMN photos BIGINT DEFAULT 0")
        self.__exec_or_ignore("ALTER TABLE user ADD COLUMN locations BIGINT DEFAULT 0")
        self.__exec_or_ignore("ALTER TABLE user ADD COLUMN herfindahl DOUBLE DEFAULT 0")
        self.__exec_or_ignore("ALTER TABLE user ADD COLUMN comments_given BIGINT DEFAULT 0")
        self.__exec_or_ignore("ALTER TABLE user ADD COLUMN comments_received BIGINT DEFAULT 0")
        self.__exec_or_ignore("ALTER TABLE user ADD COLUMN likes_given BIGINT DEFAULT 0")
        self.__exec_or_ignore("ALTER TABLE user ADD COLUMN likes_received BIGINT DEFAULT 0")

        self.__exec_or_ignore("CREATE INDEX user_username ON user (username)")
        self.__exec_or_ignore("CREATE INDEX user_active ON user (active)")

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

        self.__exec_or_ignore("CREATE INDEX likes_media ON likes (media)")
        self.__exec_or_ignore("CREATE INDEX likes_user ON likes (user)")

        # create comment table
        self.__exec_or_ignore("CREATE TABLE comment (id BIGINT PRIMARY KEY)")
        self.__exec_or_ignore("ALTER TABLE comment MODIFY id BIGINT AUTO_INCREMENT")
        self.__exec_or_ignore("ALTER TABLE comment AUTO_INCREMENT = 1000000")
        self.__exec_or_ignore("ALTER TABLE comment ADD COLUMN user BIGINT")
        self.__exec_or_ignore("ALTER TABLE comment ADD COLUMN media BIGINT")
        self.__exec_or_ignore("ALTER TABLE comment ADD COLUMN location BIGINT")
        self.__exec_or_ignore("ALTER TABLE comment ADD COLUMN ts BIGINT")

        self.__exec_or_ignore("CREATE INDEX comment_media ON comment (media)")
        self.__exec_or_ignore("CREATE INDEX comment_user ON comment (user)")

        self.conn.commit()
