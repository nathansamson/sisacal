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


import os
import flask

import coursescalendar
import sisa

app = flask.Flask(__name__)

@app.route("/")
def index():
    return flask.render_template('index.html')

@app.route("/login", methods=['POST'])
def login():
    ua_userid = flask.request.form['ua_username']
    ua_password = flask.request.form['ua_password']
    
    sisa_connection = sisa.SisA()
    try:
        sisa_connection.login(ua_userid, ua_password)
        flask.flash('U bent ingelogd en kunt uw kalender bekijken', 'notice')
        flask.session['sisa_cookies'] = sisa_connection.cookies
        return flask.redirect(flask.url_for('preview'))
    except sisa.SisALoginError as exc:
        flask.flash('Uw inloggegevens waren niet correct', 'error')
        return flask.render_template('login.html')

@app.route('/calendar/preview')
def preview():
    sisa_connection = sisa.SisA(flask.session['sisa_cookies'])

    return flask.render_template('calendar/preview.html',
                                 calendar=sisa_connection.calendar(),
                                 week_day_to_text=coursescalendar.WEEKDAY_TO_TEXT)

if __name__ == "__main__":
    app.secret_key = os.environ.get("SECRET_KEY")
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
