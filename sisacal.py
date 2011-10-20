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

import datetime
import pytz
import os
import flask

import coursescalendar
import sisa
import ical
import gcal

app = flask.Flask(__name__)
    
@app.route("/")
def index():
    return flask.render_template('index.html')

@app.route("/login", methods=['POST', 'GET'])
def login():
    if flask.request.method == 'POST':
        ua_userid = flask.request.form['ua_username']
        ua_password = flask.request.form['ua_password']
        
        sisa_connection = sisa.SisA()
        try:
            sisa_connection.login(ua_userid, ua_password)
            flask.flash('U bent ingelogd en kunt uw kalender bekijken', 'notice')
            flask.session['sisa_cookies'] = sisa_connection.cookies
            return flask.redirect(flask.url_for('preview'))
        except sisa.SisALoginError as exc:
            
            now = datetime.datetime.now(pytz.timezone('Europe/Brussels'))
            if now.hour >= 0 and now.hour < 5:
                flask.flash('SisA is niet bereikbaar midden in de nacht. Probeer het morgen opnieuw.', 'notice')
            else:
                flask.flash('We konden u niet inloggen. "%s"' % str(exc), 'notice');
            
            return flask.render_template('login.html')
    else:
        return flask.render_template('login.html')

@app.route('/calendar/preview')
def preview():
    sisa_connection = sisa.SisA(flask.session['sisa_cookies'])

    try:
        google_cal = gcal.GoogleCalendar(google_auth_token())
        return flask.render_template('calendar/preview.html',
                                     calendar=sisa_connection.calendar(),
                                     week_day_to_text=coursescalendar.WEEKDAY_TO_TEXT,
                                     google_export_url=google_cal.generate_login_url(
                                        flask.request.url_root[0:-1] + flask.url_for('list_google_calendars')))
    except sisa.SisALoginError as exc:
        flask.flash('Uw kalender kon niet worden weergegeven "%s"' % str(exc), 'error')
        return flask.render_template('login.html')

@app.route('/export/ical')
def export_ical():

    sisa_connection = sisa.SisA(flask.session['sisa_cookies'])

    try:
        ical_export = ical.ICal(sisa_connection.calendar())
        
        resp = flask.make_response(ical_export.export())
        resp.headers['Content-Disposition'] = 'attachment; filename="ical.ics"'
        resp.headers['Content-Type'] = 'text/calendar; charset=UTF-8'
        return resp
    except sisa.SisALoginError as exc:
        flask.flash('Uw kalender kon niet worden opgeslagen "%s"' % str(exc), 'error')
        return flask.redirect(flask.url_for('login'))

def google_auth_token():
    if 'gcal-auth-token' in flask.session:
        return flask.session['gcal-auth-token']
    else:
        return None

@app.route("/export/google/list_calendars")
def list_google_calendars():
    google_cal = gcal.GoogleCalendar(auth_token=google_auth_token())
    if 'token' in flask.request.args:
        auth_token = google_cal.authenticate(flask.request.url)
    
        if auth_token == False:
            flask.flash('We konden u niet authenticeren.', 'error')
            return flask.redirect(flask.url_for('preview'))
    
        flask.session['gcal-auth-token'] = auth_token
        return flask.redirect(flask.url_for('list_google_calendars'))
    
    calendars = google_cal.get_own_calendars()
    if calendars == None:
        flask.flash('Kon google calendar niet bereiken', 'error')
        return flask.redirect(flask.url_for('preview'))
    
    return flask.render_template("google/calendar-list.html",
                                 calendars=calendars)

@app.route("/export/google/save", methods=['POST'])
def google_export_calendar():
    google_cal = gcal.GoogleCalendar(auth_token=google_auth_token())
    sisa_connection = sisa.SisA(flask.session['sisa_cookies'])
    
    try:
        export_cal = sisa_connection.calendar()
    except:
        flask.flash('Uw sessie is verlopen, log opnieuw in.', 'error')
        return flask.redirect(flask.url_for('login'))

    
    form = flask.request.form
    if 'new-calendar' in form and form['new-calendar'].strip() != "":    
        exported, error = google_cal.export(export_cal, new_calendar_title=form['new-calendar'].strip())
    elif 'old-calendar' in form and form['old-calendar'] != "":
        exported, error = google_cal.export(export_cal, calendar_id=form['old-calendar'])
    
    if exported:
        flask.flash('Uw kalender werd overgezet naar Google Calendar', 'notice')
        return flask.redirect(flask.url_for('preview'))
    else:
        flask.flash('Uw kalender kon niet worden opgeslagen. Probeer nog eens opnieuw. ("%s")' % error, 'error')
        return flask.redirect(flask.url_for('list_google_calendars'))


if __name__ == "__main__":
    app.debug = True
    app.secret_key = os.environ.get("SECRET_KEY")
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
