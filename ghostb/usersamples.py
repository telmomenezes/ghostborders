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


import numpy as np
from random import randrange


class UserSamples:
    def __init__(self, db, region, userscales_file):
        self.db = db
        self.region = region

        self.data = np.genfromtxt(userscales_file, names=True, delimiter=',')
        self.scales = len(self.data[0]) - 3

    def row2category(self, row):
        category = ''
        for s in range(self.scales):
            if row[s + 3] > 0:
                category += str(s + 1)
        return category

    def username(self, user_id):
        self.db.cur.execute("SELECT username FROM user WHERE id=%s", (user_id,))
        res = self.db.cur.fetchall()
        return res[0][0]

    def random_samples(self, users, n):
        samples = []
        for i in range(n):
            index = randrange(0, len(users))
            samples.append(users[index])
        samples = [self.username(u) for u in samples]
        return samples

    def html(self, title, body):
        return """
        <!DOCTYPE html>
        <html lang="en">

        <head>
            <meta charset="utf-8">
            <title>
                %s
            </title>
        </head>

        <body>
            %s
        </body>

        </html>
        """ % (title, body)

    def generate(self):
        cats = {}
        for row in self.data:
            user_id = int(row[0])
            cat = self.row2category(row)
            if cat in cats:
                cats[cat].append(user_id)
            else:
                cats[cat] = [user_id]

        title = '%s samples' % self.region
        body = '<h1>%s samples</h1>' % self.region
        for cat in cats:
            body += '<h2>Scales %s</h2>' % cat
            samples = self.random_samples(cats[cat], 15)
            for sample in samples:
                body += '<a href="https://www.instagram.com/%s/">%s</a>' % (sample, sample)
            body += '<br>'
        print(self.html(title, body))
