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


from instagram.client import InstagramAPI
from instagram.bind import InstagramClientError
from datetime import datetime
import calendar
import time


class Retriever:

    def __init__(self, config, db):
        self.config = config
        self.api = InstagramAPI(
            client_id=config.data['instagram']['client_id'], client_secret=config.data['instagram']['client_secret'])
        self.db = db

    def add_user(self, user_id, username):
        self.db.cur.execute("SELECT username FROM user WHERE id=%s", (user_id,))
        row = self.db.cur.fetchone()
        if row is None:
            self.db.cur.execute("INSERT INTO user (id, username) VALUES (%s, %s)", (user_id, username))
            self.db.conn.commit()

    def media_id(self, user_id, loc_id, ts, lat, lng, ig_id):
        self.db.cur.execute("SELECT id FROM media WHERE ig_id=%s", (ig_id,))
        row = self.db.cur.fetchone()
        if row is None:
            self.db.cur.execute(
                "INSERT INTO media (user, location, ts, lat, lng, ig_id) VALUES (%s, %s, %s, %s, %s, %s)",
                (user_id, loc_id, ts, lat, lng, ig_id))
            media_id = self.db.cur.lastrowid
            self.db.conn.commit()
        else:
            media_id = row[0]

        return media_id

    def add_like(self, user_id, media_id):
        self.db.cur.execute("SELECT id FROM likes WHERE user=%s and media=%s", (user_id, media_id))
        row = self.db.cur.fetchone()
        if row is None:
            self.db.cur.execute("INSERT INTO likes (user, media) VALUES (%s, %s)", (user_id, media_id))
            self.db.conn.commit()

    def add_comment(self, user_id, media_id):
        self.db.cur.execute("SELECT id FROM comment WHERE user=%s and media=%s", (user_id, media_id))
        row = self.db.cur.fetchone()
        if row is None:
            self.db.cur.execute("INSERT INTO comment (user, media) VALUES (%s, %s)", (user_id, media_id))
            self.db.conn.commit()

    def loc_min_ts(self, loc_id):
        self.db.cur.execute("SELECT min_ts FROM location WHERE id=%s", (loc_id,))
        row = self.db.cur.fetchone()
        min_ts = row[0]
        return min_ts

    def set_loc_min_ts(self, loc_id, min_ts):
        self.db.cur.execute("UPDATE location SET min_ts=%s WHERE id=%s", (min_ts, loc_id))
        self.db.conn.commit()

    def query_point_step(self, lat, lng, loc_id, min_ts, max_ts):
        # throttle
        time.sleep(0.5)

        min_dt = datetime.max

        try:
            medias = self.api.media_search(
                q="", distance=5000, count=1000, lat=lat, lng=lng, min_timestamp=min_ts, max_timestamp=max_ts)
        except InstagramClientError as e:
            print(e)
            if e.status_code == "500":
                return max_ts  # give up on this location
            raise InstagramClientError(e.error_message, e.status_code)

        count = 0
        for m in medias:
            try:
                lat = m.location.point.latitude
                lng = m.location.point.longitude
                ig_id = m.id
                ts = calendar.timegm(m.created_time.utctimetuple())
                user_id = m.user.id

                self.add_user(user_id, m.user.username)

                media_id = self.media_id(user_id, loc_id, ts, lat, lng, ig_id)

                if m.created_time < min_dt:
                    min_dt = m.created_time

                    for u in m.likes:
                        self.add_user(u.id, u.username)
                        self.add_like(u.id, media_id)

                        for c in m.comments:
                            self.add_user(c.user.id, c.user.username)
                            self.add_comment(c.user.id, media_id)
                count += 1
            except AttributeError as e:
                print("attribute missing: %s" % e)
        
        print('retrived photos: %s' % count)
        print('date: %s' % min_dt)
        if len(medias) > 0:
            q_min_ts = calendar.timegm(min_dt.utctimetuple())
        else:
            q_min_ts = max_ts

        return q_min_ts

    def query_point(self, lat, lng, loc_id, min_ts, max_ts):
        q_last_min_ts = -1
        q_max_ts = self.loc_min_ts(loc_id)
        if q_max_ts < 0:
            q_max_ts = max_ts
        q_min_ts = self.query_point_step(lat, lng, loc_id, min_ts, q_max_ts)
        self.set_loc_min_ts(loc_id, q_min_ts)

        while q_min_ts != q_last_min_ts:
            q_last_min_ts = q_min_ts
            q_min_ts = self.query_point_step(lat, lng, loc_id, min_ts, q_min_ts)
            self.set_loc_min_ts(loc_id, q_min_ts)

    def run_once(self):
        self.db.cur.execute("SELECT id, name, lat, lng FROM location WHERE done=0")
        rows = self.db.cur.fetchall()

        count = 0

        min_ts = self.config.data['time_range']['min_ts']
        max_ts = self.config.data['time_range']['max_ts']

        for row in rows:
            count += 1
            print(count, row[1])
            self.query_point(row[2], row[3], row[0], min_ts, max_ts)

            self.db.cur.execute("UPDATE location SET done=1 WHERE id=%s", (row[0],))
            self.db.conn.commit()

        return True

    def run(self):
        done = False
        while not done:
            try:
                done = self.run_once()
            except KeyboardInterrupt:
                print('interrupted by user.')
                done = True
            except Exception as e:
                print(e)
        print('done.')
