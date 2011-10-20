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

import yaml

class Location:
	CAMPUS = 0
	BUILDING = 1
	AULA = 2

	def __init__(self, name, info=None,
	             street=None, coords=None,
			     campus=None, building=None, aula=None):
		self.name = name
		self.info = info
		self.street = street
		self.coords = coords
		self.campus_name = campus
		self.building_name = building
		self.aula_name = aula
	
	def export_name(self):
		if self.street:
			return "%s - %s - %s" % (self.name, self.full_name(False), self.street)
		elif self.campus_name:
			return "%s - %s" % (self.name, self.full_name(False))
		else:
			return self.name
	
	def full_name(self, repeat_basic_info=True):
		if self.info != None:
			campus = self.campus_name if self.campus_name else self.info[Location.CAMPUS]
			if self.aula_name:
				if repeat_basic_info:
					return "%s %s (%s.%s)" % (campus, self.aula_name,
				        	                  self.info[Location.BUILDING],
				         	                  self.info[Location.AULA])
				else:
					return "%s %s" % (campus, self.aula_name)
			elif self.building_name:
				if repeat_basic_info:
					return "%s %s %s" % (campus, self.building_name, self.info[Location.AULA])
				else:
					return "%s %s" % (campus, self.building_name)
			else:
				if repeat_basic_info:
					return "%s %s %s" % (campus, self.info[Location.BUILDING], self.info[Location.AULA])
				else:
					return "%s" % (campus)
		else:
			return self.name

class LocationFinder:
	def __init__(self, input_file):
		self.locations = {}
		with open(input_file) as f:
			self.locations = yaml.load(f.read())
		
	def find(self, location):
		if location == '-':
			return Location(name='Onbekend')

		parts = location.split('.')
		if len(parts) != 3:
			return Location(name=location)
		
		campus, building, aula = parts
		
		if campus not in self.locations:
			return Location(location)
		
		if 'name' in self.locations[campus]:
			campus_name = self.locations[campus]['name']
		else:
			campus_name = None
		
		info = (campus, building, aula)
		
		if building not in self.locations[campus]['buildings']:
			return Location(location, info, campus=campus_name)
		
		if 'street' in self.locations[campus]['buildings'][building]:
			street = self.locations[campus]['buildings'][building]['street']
		else:
			street = None
		
		if 'coords' in self.locations[campus]['buildings'][building]:
			coords = self.locations[campus]['buildings'][building]['coords']
		else:
			coords = None
		
		if 'name' in self.locations[campus]['buildings'][building]:
			building_name = self.locations[campus]['buildings'][building]['name']
		else:
			building_name = None
	
		if aula not in self.locations[campus]['buildings'][building]['aulas']:
			return Location(location, info,
			                campus=campus_name, building=building_name,
			                coords=coords, street=street)
		
		name = self.locations[campus]['buildings'][building]['aulas'][aula]
		return Location(location, info,
		                campus=campus_name, building=building_name,
			            coords=coords, street=street, aula=name)
