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
import flask

import atom
import gdata.gauth
import gdata.calendar.client
import gdata.calendar.service


class GoogleCalendar():
    SCOPES = ['http://www.google.com/calendar/feeds/']

    def __init__(self, auth_token=None):
        self.calendar_client = gdata.calendar.client.CalendarClient(source="SisACal")
        
        if auth_token:
            self.calendar_client.auth_token = gdata.gauth.AuthSubToken(
                    auth_token,
                    GoogleCalendar.SCOPES)
    
    def generate_login_url(self, return_url):
        if self.calendar_client.auth_token:
            return return_url
        return gdata.gauth.generate_auth_sub_url(return_url,
                                                 GoogleCalendar.SCOPES,
                                                 session=True)
    
    def authenticate(self, url):
        try:
            self.calendar_client.auth_token = gdata.gauth.AuthSubToken.from_url(url)
            self.calendar_client.auth_token = self.calendar_client.upgrade_token()
            
            return self.calendar_client.auth_token.token_string
        except ValueError as e:
            return False
    
    def get_own_calendars(self):
        try:
            return self.calendar_client.get_own_calendars_feed().entry
        except gdata.client.Unauthorized:
            return None
    
    def export(self, cal_to_export, calendar_id=None, new_calendar_title=None):
        try:
            if new_calendar_title != None:
                calendar = gdata.calendar.data.CalendarEntry()
                calendar.title = atom.data.Title(text=new_calendar_title)
                calendar.timezone = gdata.calendar.data.TimeZoneProperty(value="Europe/Brussels")
                calendar.hidden = gdata.calendar.data.HiddenProperty(value='false')
                calendar.color = gdata.calendar.data.ColorProperty(value='#5C1158')
                calendar = self.calendar_client.insert_calendar(new_calendar=calendar)
                
                if calendar.content == None:
                    return False, 'Kon kalender niet maken'
                cal_src = calendar.content.src
            else:
                cal_src = calendar_id

            batch_feed = gdata.calendar.data.CalendarEventFeed()
            
            for course in cal_to_export.courses:
                for contact in course.contact_moments:
                    for datetimes in contact.datetimes():
                        new_event_entry = gdata.calendar.data.CalendarEventEntry()
                        new_event_entry.title = atom.data.Title(text='%s - %s %s' % (course.name, contact.course_part, contact.docent))
                        start_time = datetimes['start'].isoformat('T')
                        end_time = datetimes['end'].isoformat('T')
                        
                        new_event_entry.when.append(gdata.calendar.data.When(start=start_time, end=end_time))
                        batch_feed.add_insert(new_event_entry)
            
            response = self.calendar_client.execute_batch(batch_feed, cal_src + "/batch")
                                               
            for entry in response.entry:
                if not (int(entry.batch_status.code) >= 200 and 
                        int(entry.batch_status.code) <300):
                    return False, 'Kon niet alles opslaan.'
            return True, ''
        except gdata.client.RequestError as e:
            return False, 'Kon google niet contacteren (\'%s\')' % str(e)
