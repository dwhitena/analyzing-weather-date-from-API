import pandas as pd
from pandas.io.json import json_normalize
import datetime
import requests
import sqlite3 as lite


# -----------
# DEFINITIONS
# -----------

# define the locations of cities for this analysis
cities = {"Chicago": ["41.837551","-87.681844"], 
     "New_York_City": ["40.663619","-73.938589"],
     "Denver": ["39.761850","-104.881105"],
     "Los_Angeles": ["34.019394","-118.410825"],
     "Austin": ["30.303936","-97.754355"]}

# dark sky forecasting API
apikey = "2d788ea8b4b010ec1bd77776d96363ae"
url = "https://api.forecast.io/forecast/" + apikey + "/"

# start date for this analysis (30 whole days ago)
start_date = datetime.datetime.now() 
start_date = datetime.datetime.combine(start_date.date(), datetime.time(0))
start_date = start_date - datetime.timedelta(days=30)


# -----------------------
# RETRIEVE AND STORE DATA
# -----------------------


# connect to database
con = lite.connect('weather.db')
cur = con.cursor()

# construct an array of the analyzed dates 
dateinc = []
dateinc.append(start_date)
for i in range(29):
	dateinc.append(dateinc[-1] + datetime.timedelta(days=1))
dateincstr = [(num.strftime('%s'),) for num in dateinc] 

# construct table
city_ids = [x + ' NUMERIC' for x in cities.keys()]
with con:
	# clear table if it exists
	cur.execute("DROP TABLE IF EXISTS maxtemps")
	# create maxtemps table
	cur.execute("CREATE TABLE maxtemps ( day INT, " +  ", ".join(city_ids) + ");")
	# fill dates
	cur.executemany('INSERT INTO maxtemps (day) VALUES (?)', dateincstr)


# loop over cities
for city in cities.keys():
	# loop over days
	for i in range(30):

		# api call
		apicall = url + cities[city][0] + "," + cities[city][1] + "," + dateinc[i].strftime('%s')
		r = requests.get(apicall)

		# get max temp
		maxtemp = float(json_normalize(r.json()['daily']['data'])['temperatureMax'])


		# store max temp
		with con:
			cur.execute("UPDATE maxtemps SET " + city + "=" + \
				str(maxtemp) + " WHERE day = " + dateinc[i].strftime('%s') + ";")



# construct API call
#apicall = url + cities["Chicago,IL"][0] + "," + cities["Chicago,IL"][1] + "," + start_datestr

# get Citibike data:
#r = requests.get(apicall)

# print max temperature
#print json_normalize(r.json()['daily']['data'])['temperatureMax']