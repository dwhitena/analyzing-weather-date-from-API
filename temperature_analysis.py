import pandas as pd
from pandas.io.json import json_normalize
import datetime
import requests
import sqlite3 as lite
import collections
import folium


# define the locations of cities for this analysis
cities = {"Chicago": ["41.837551","-87.681844"], 
     "New_York_City": ["40.663619","-73.938589"],
     "Denver": ["39.761850","-104.881105"],
     "Los_Angeles": ["34.019394","-118.410825"],
     "Austin": ["30.303936","-97.754355"]}

# connect to database
con = lite.connect('weather.db')
cur = con.cursor()

# read the weather data into a dataframe
df = pd.read_sql_query("SELECT * FROM maxtemps ORDER BY day", con)

# convert the dates to datetime objects and set this column
# as the index
pd.to_datetime(df['day'], unit='s')
df.set_index('day', drop=True, inplace=True)


# ----------------------------------------
# CALCULATE LARGEST AGGREGATE TEMP CHANGES
# ----------------------------------------

# calculate the total (abs value) change in temperatures
# for each city
total_change = collections.defaultdict(int)
# loop over cities
for column in df.columns:
	# list of daily max temps for the particular city
	citytemplist = df[column].tolist()
	# aggregate change
	tempchange = 0;
	for i in range(len(citytemplist)-1):
		tempchange += abs(citytemplist[i] - citytemplist[i+1])
		total_change[column] = tempchange

# find the station with the max activity
max_temprange = max(total_change, key=total_change.get)

print "The city with the highest changes in maximum temperature is: " + max_temprange
print "with an aggregate change in temperature of: " + str(total_change[max_temprange]) + " degrees over the past thirty days."


# ----------------------------------------
# CALCULATE LARGEST DAY-TO-DAY TEMP SWING
# ----------------------------------------

# calculate the highest (abs value) day-to-day change in temperatures
# for each city
swing_change = collections.defaultdict(int)
# loop over cities
for column in df.columns:
	# list of daily max temps for the particular city
	citytemplist = df[column].tolist()
	# aggregate change
	swing_change[column] = 0
	for i in range(len(citytemplist)-1):
		tempchange = abs(citytemplist[i] - citytemplist[i+1])
		if swing_change[column] < tempchange:
			swing_change[column] = tempchange

# find the station with the max activity
max_swing = max(swing_change, key=swing_change.get)

print "The city with the largest day-to-day temperature swing was: " + max_swing
print "with an day-to-day swing of: " + str(swing_change[max_swing]) + " degrees."


# ---------------------
# VISUALIZE RESULTS
# ---------------------

# visualize aggregate changes on us map
map_2 = folium.Map(location=[40, -98], width=750, height=500, zoom_start=4)
for k in cities.keys():
	area = total_change[k]*1000
	map_2.circle_marker(location=cities[k], radius=area,
                    popup=k + ": " + str(total_change[k]) + " degrees", line_color='#3186cc',
                    fill_color='#3186cc')
map_2.create_map(path='agg_temp_changes_map.html')

# visualize day-to-day swings on us map
map_2 = folium.Map(location=[40, -98], width=500, height=500, zoom_start=4)
for k in cities.keys():
	area = swing_change[k]*7000
	map_2.circle_marker(location=cities[k], radius=area,
                    popup=k + ": " + str(swing_change[k]) + " degrees", line_color='#3186cc',
                    fill_color='#3186cc')
map_2.create_map(path='swing_temp_changes_map.html')