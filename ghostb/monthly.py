import calendar
import datetime
import time


def month_start(month):
    parts = month.split('-')
    y = int(parts[0])
    m = int(parts[1])

    date = datetime.date(y, m, 1)
    return time.mktime(date.timetuple())


def month_end(month):
    parts = month.split('-')
    y = int(parts[0])
    m = int(parts[1])
  
    d = calendar.monthrange(y, m)[1]
    date = datetime.date(y, m, d)
    date += datetime.timedelta(days=1)
    return time.mktime(date.timetuple())


def ts2year_month(ts):
    dt = datetime.datetime.fromtimestamp(ts)
    return dt.strftime('%Y-%m')


class Monthly:
    def __init__(self, db):
        self.db = db
        self.table = {}

    def __inc_field(self, month, field):
        if month not in self.table:
            self.table[month] = {'first_ts': 0, 'last_ts': 0}
        self.table[month][field] += 1

    def __process_user(self, user):
        first_ts = user[0]
        last_ts = user[1]
        if first_ts and (first_ts > 0):
            month = ts2year_month(first_ts)
            self.__inc_field(month, 'first_ts')
            month = ts2year_month(last_ts)
            self.__inc_field(month, 'last_ts')

    def write_month_table(self):
        for month in self.table:
            first_seen = self.table[month]['first_seen']
            last_seen = self.table[month]['last_seen']
            self.db.cur.execute("INSERT INTO month (id, first_seen_users, last_seen_users) VALUES (%s, %s , %s)"
                                % (month, first_seen, last_seen))
    
        self.db.conn.commit()

    def generate(self):
        self.db.cur.execute("SELECT count(id) FROM user")
        nusers = self.db.cur.fetchone()[0]
    
        print("%s users to process" % nusers)

        n = 0
        self.table = {}

        while True:
            self.db.cur.execute("SELECT first_ts, last_ts, photos FROM user LIMIT %s,1000" % n)
            users = self.db.cur.fetchall()
      
            if len(users) == 0:
                break
            else:
                percent = float(n) / float(nusers) * 100.0
                n += len(users)
                for user in users:
                    self.__process_user(user)
                print("%s/%s (%s%%) processed" % (n, nusers, percent))

        self.write_month_table()
        print("done.")

    def update_photos_month(self):
        self.db.cur.execute("SELECT id FROM month")
        months = self.db.cur.fetchall()
        for m in months:
            month = m[0]
            ts0 = month_start(month)
            ts1 = month_end(month)
            self.db.cur.execute("SELECT count(id) AS cm FROM media WHERE ts >= %s AND ts < %s" % (ts0, ts1))
            q = self.db.cur.fetchall()
            photos = q[0][0]
            print("%s %s" % (month, photos))
            self.db.cur.execute("UPDATE month SET photos=%s WHERE id=%s" % (photos, month))

        print("done.")

    def print_months(self):
        print("month,first_seen,last_seen,photos")
        self.db.cur.execute("SELECT id,first_seen_users,last_seen_users,photos FROM month ORDER BY id")
        months = self.db.cur.fetchall()
        for month in months:
            print("%s,%s,%s,%s" % month)
