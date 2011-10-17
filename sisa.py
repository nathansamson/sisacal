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
import requests
from lxml import etree
from lxml.html import soupparser

import coursescalendar

class SisALoginError(Exception):
    pass

class SisA():
    __LOGIN_URL = "https://sisastudent.ua.ac.be/psp/studweb/EMPLOYEE/HRMS/c/SA_LEARNER_SERVICES.SSS_STUDENT_CENTER.GBL?cmd=login&languageCd=DUT"
    __CHANGE_CORRECT_CALENDAR_URL = "https://sisastudent.ua.ac.be/psc/studweb/EMPLOYEE/HRMS/c/SA_LEARNER_SERVICES.SSR_SSENRL_SCHD_W.GBL"
    __CALENDAR_URL = "https://sisastudent.ua.ac.be/psc/studweb/EMPLOYEE/HRMS/c/SA_LEARNER_SERVICES.SSR_SSENRL_LIST.GBL?Page=SSR_SSENRL_LIST&Action=A&ACAD_CAREER=MASA&EMPLID=20081398&INSTITUTION=00001&STRM=2110"
    
    __PERMANENT_REDIRECT = 302

    def __init__(self, cookies={}):
        self.cookies = cookies

    def login(self, username, password):
        self.cookies = {}
        login = requests.post(SisA.__LOGIN_URL, params={'timezoneOffset': 0,
                                                        'userid': username,
                                                        'pwd': password},
                                         cookies=self.cookies)
        self.cookies = login.cookies
        
        if 'PS_TOKEN' in login.cookies:
            return True
        else:
            raise SisALoginError()

    def calendar(self):
        raise SisALoginError()
        if not 'PS_TOKEN' in self.cookies:
            raise SisALoginError()
        
        r = requests.get(SisA.__CALENDAR_URL, cookies=self.cookies)
    
        r = requests.post(SisA.__CHANGE_CORRECT_CALENDAR_URL, cookies=r.cookies,
                          params={'ICAction': 'DERIVED_REGFRM1_SSR_SCHED_FORMAT$35$',
                                  'DERIVED_REGFRM1_SSR_SCHED_FORMAT$35$': 'L'})
    
        r = requests.get(SisA.__CALENDAR_URL, cookies=r.cookies)
        self.cookies = r.cookies

        html = soupparser.fromstring(r.content)
        
        if len(html.xpath('//table[@id="WEEKLY_SCHED_HTMLAREA"]')) > 0:
            raise SisALoginError()
        
        courses = html.xpath('//table[.//td[@class="PAGROUPDIVIDER"]][@class="PSGROUPBOXWBO"]')
        
        calendar = coursescalendar.CoursesCalendar()
        
        for course_table in courses:
            course_id = course_table.xpath('.//tr[1]/td/text()')[0]
            course_name = course_id.split('-')[1]
        
            course = calendar.add_course(course_id, course_name)
            
            contact_table = course_table.xpath('.//table[starts-with(@id, "CLASS_MTG_VW$scroll$")]')[0]
            course_part = 'Onbekend'
            for contact_moment_row in contact_table.xpath('.//tr[position() > 1]'):
                xpath = contact_moment_row.xpath
                course_part_potential = xpath('td[3]/span/text()')[0]
                if len(course_part_potential.strip()) > 0:
                   course_part = course_part_potential
                time_part = xpath('td[4]/span/text()')[0]
                location = xpath('td[5]/span/text()')[0]
                docent = ''.join(xpath('td[6]/span/text()'))
                
                week_data = xpath('td[8]/span/text()')[0]
                
                # If time info is not available don't add it..
                if len(time_part.strip()) == 0 or time_part.strip() == '-':
                    continue
                
                week_day_dutch, hours = time_part.split(' ', 1)
                if week_day_dutch == 'Maandag':
                    week_day = coursescalendar.MONDAY
                elif week_day_dutch == 'Dinsdag':
                    week_day = coursescalendar.TUESDAY
                elif week_day_dutch == 'Woensdag':
                    week_day = coursescalendar.WEDNESDAY
                elif week_day_dutch == 'Donderdag':
                    week_day = coursescalendar.THURSDAY
                elif week_day_dutch == 'Vrijdag':
                    week_day = coursescalendar.FRIDAY
                elif week_day_dutch == 'Zaterdag':
                    week_day = coursescalendar.SATERDAY
                elif week_day_dutch == 'Zondag':
                    week_day = coursescalendar.SUNDAY
                
                start_hour_str, end_hour_str = hours.split(' - ', 1)
                start_hour = datetime.time(int(start_hour_str.split(':', 1)[0]),
                                           int(start_hour_str.split(':', 1)[1]))
                
                end_hour = datetime.time(int(end_hour_str.split(':', 1)[0]),
                                         int(end_hour_str.split(':', 1)[1]))
                
                
                start_week_str, end_week_str = week_data.split(' - ', 1)
                start_week = datetime.datetime.strptime(start_week_str, '%d/%m/%Y')
                end_week = datetime.datetime.strptime(end_week_str, '%d/%m/%Y')
                
                contact_moment = course.add_contact_moment(course_part,
                                    week_day,
                                    start_hour, end_hour,
                                    start_week.date(), end_week.date(),
                                    location, docent)
        return calendar
