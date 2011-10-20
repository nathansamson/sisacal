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
import string

MONDAY = 1
TUESDAY = 2
WEDNESDAY = 3
THURSDAY = 4
FRIDAY = 5
SATURDAY = 6
SUNDAY = 7

WEEKDAY_TO_TEXT = {
    MONDAY: 'Maandag',
    TUESDAY: 'Dinsdag',
    WEDNESDAY: 'Woensdag',
    THURSDAY: 'Donderdag',
    FRIDAY: 'Vrijdag',
    SATURDAY: 'Zaterdag',
    SUNDAY: 'Zondag',
}

class ContactMoment(object):
    def __init__(self, course_part,
                       week_day,
                       start_hour, end_hour,
                       weeks, location, docent):
        self.course_part = course_part
        self.week_day = week_day
        self.start_hour = start_hour
        self.end_hour = end_hour
        self.weeks = weeks
        self.location = location
        self.docent = docent

    def datetimes(self):
        datets = []
        for week in self.weeks:
            day_str = '-'.join([str(i) for i in week]) + '-' + str(self.week_day % 7)
            day = datetime.datetime.strptime(day_str, '%Y-%W-%w')

            start = pytz.timezone('Europe/Brussels').localize(
                        datetime.datetime(day.year, day.month, day.day,
                                          self.start_hour.hour, self.start_hour.minute))
            end = pytz.timezone('Europe/Brussels').localize(
                        datetime.datetime(day.year, day.month, day.day,
                                          self.end_hour.hour, self.end_hour.minute))

            datet = {'start': start, 'end': end}
            datets.append(datet)
        
        return datets

    def days(self):
        return [datet['start'].date() for datet in self.datetimes()]
            
    def merge(self, other):
        for attr in ['course_part', 'week_day',
                     'start_hour', 'end_hour', 'docent']:
            if self.__dict__[attr] != other.__dict__[attr]:
                return False
        
        if self.location.name != other.location.name:
            return False
        
        self.weeks.extend(other.weeks)
        
        return True

class Course(object):
    def __init__(self, code, name):
        self.code = code
        self.name = name
        self.contact_moments = []
    
    def add_contact_moment(self, course_part,
                                 week_day,
                                 start_hour, end_hour,
                                 start_week_date, end_week_date,
                                 location, docent):
        start_week = start_week_date.isocalendar()[0:2]
        end_week = end_week_date.isocalendar()[0:2]
        
        if end_week[0] > start_week[0]:
            raise Exception("Courses that go around a year are not yet supported")
        weeks = [[start_week[0], week] for week in range(start_week[1], 
                                                         end_week[1]+1)]
        
        contact_moment = ContactMoment(course_part,
                                       week_day,
                                       start_hour, end_hour,
                                       weeks, location, docent)
        merged = False
        for other_contact_moment in self.contact_moments:
            if other_contact_moment.merge(contact_moment):
                merged = True

                break
        if merged:
            return other_contact_moment
        else:
            self.contact_moments.append(contact_moment)
            return contact_moment
    
    def id(self):
        invalid = '&"\' \t\n\r'
        table = string.maketrans(invalid, '-' * len(invalid))
        return str(self.code).lower().translate(table)

class CoursesCalendar:
    def __init__(self):
        self.courses = []

    def add_course(self, course_code, course_name):
        course = Course(course_code, course_name)
        self.courses.append(course)
        return course
