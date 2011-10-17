# This file is part of SisACal.

# SisACal is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# SisACal is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with SisACal.  If not, see <http://www.gnu.org/licenses/>.

import flask

class ICal():
    def __init__(self, calendar):
        self.calendar = calendar

    def export(self):
        return flask.render_template('export/ical.ics',
                                     calendar=self.calendar)
