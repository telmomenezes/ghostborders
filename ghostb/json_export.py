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


import json
import progressbar


class JsonExport:
    def __init__(self, db, outfile):
        self.db = db
        self.outfile = outfile

    def export(self):
        print('exporting to json file: %s' % self.outfile)

        self.db.cur.execute("SELECT count(id) FROM media")
        nmedia = self.db.cur.fetchone()[0]

        with open(self.outfile, 'w') as f:
            with progressbar.ProgressBar(max_value=nmedia) as bar:
                done = False
                n = 0
                while not done:
                    self.db.cur.execute("SELECT id, user, location, ts, lat, lng, ig_id FROM media LIMIT %s,1000" % n)
                    medias = self.db.cur.fetchall()
                    if len(medias) == 0:
                        done = True
                    else:
                        for media in medias:
                            media_data = {'id': media[0],
                                          'user': media[1],
                                          'location': media[2],
                                          'ts': media[3],
                                          'lat': media[4],
                                          'lng': media[5],
                                          'id_id': media[6]}
                            f.write('%s\n' % json.dumps(media_data))
                        n += len(medias)
                        bar.update(n)
