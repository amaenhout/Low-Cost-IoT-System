import pandas as pd
import matplotlib.pyplot as plt
from pandas.io.json import json_normalize
import requests
import seaborn as sns
import numpy as np
import datetime

def getdata(url):
	res = requests.get(url)
	data = res.json()

	df_api = json_normalize(data)
	return df_api

# 4.2 ---------------------- BATTERY LEVEL  ----------------------
url  = 'http://127.0.0.1:5000/api/table?table=ttn_env&week=33&filter=0'
data_w1 = getdata(url)
data_w1
url  = 'http://127.0.0.1:5000/api/table?table=ttn_env&week=34&filter=0'
data_w2 = getdata(url)
data = data_w1.append(data_w2)

loc = data.loc[:,["dev_id","battery","time"]]
plotall = loc.groupby(["dev_id","time"])["battery"].mean().unstack("dev_id")
plotall.index = pd.to_datetime(plotall.index)

plotall.plot(title='Battery Level After 12 days')


# 4.3.1 ---------------------- ENV  ----------------------
# TEMP SAME LOCATION  -> WEEK 30!
url  = 'http://127.0.0.1:5000/api/table?table=ttn_env&week=30&filter=1'
data = getdata(url)

loc = data.loc[:,["dev_id","battery","time"]]
plotall = loc.groupby(["dev_id","time"])["temperature"].mean().unstack("dev_id")
plotall.index = pd.to_datetime(plotall.index)
d = plotall.loc['2019-07-22':'2019-07-23']
plotall.plot(title='Temperature Differences')
plotall
df =d.T.describe().T
df["std"].plot(title='Temperature Standard Deviation')

#Light standard deviation 
loc = data.loc[:,["dev_id","light","time"]]
plotall = loc.groupby(["dev_id","time"])["light"].mean().unstack("dev_id")
plotall.index = pd.to_datetime(plotall.index)
d = plotall.loc['2019-07-22':'2019-07-23']
d.plot()

df =d.T.describe().T
df["std"].plot()

# OVERVIEW LAST TWO WEEKS
url  = 'http://127.0.0.1:5000/api/table?table=ttn_env&week=33&filter=0'
data_w1 = getdata(url)
data_w1
url  = 'http://127.0.0.1:5000/api/table?table=ttn_env&week=34&filter=0'
data_w2 = getdata(url)
data = data_w1.append(data_w2)

# Temperature
loc = data.loc[:,["dev_id","temperature","time"]]
plotall = loc.groupby(["dev_id","time"])["temperature"].mean().unstack("dev_id")
plotall.index = pd.to_datetime(plotall.index)
plotall.plot(title='Temperature Last 2 weeks',legend=reversed)

#Light
loc = data.loc[:,["dev_id","light","time"]]
plotall = loc.groupby(["dev_id","time"])["light"].mean().unstack("dev_id")
plotall.index = pd.to_datetime(plotall.index)
plotall.plot(title='Light Last 2 weeks')


# ---------------------- MOT ----------------------
url  = 'http://127.0.0.1:5000/api/table?table=ttn_mot&week=34&filter=1'
data = getdata(url)
loc = data.loc[:,["dev_id","value","time"]]
plotall = loc.groupby(["dev_id","time"])["value"].sum().unstack("dev_id")
plotall = plotall.fillna(0)
plotall.index = pd.to_datetime(plotall.index)
plotall.plot(title='Motion Movement 1 week')

t = plotall[["ttn_mot_004"]]
t["day"] = t.index.weekday_name
t["hour"] = t.index.hour


heat = t.pivot("day", "hour", "ttn_mot_004").fillna(0)
ax = sns.heatmap(heat,robust=True, fmt="f", cmap='RdBu_r', vmin=0, vmax=60)

# ---------------------- PIR ----------------------
url  = 'http://127.0.0.1:5000/api/table?table=ttn_pir&week=33&filter=0'
data_w1 = getdata(url)
data_w1
url  = 'http://127.0.0.1:5000/api/table?table=ttn_pir&week=34&filter=0'
data_w2 = getdata(url)
data = data_w1.append(data_w2)

loc = data.loc[:,["dev_id","value","time"]]
plotall = loc.groupby(["dev_id","time"])["value"].sum().unstack("dev_id")
plotall = plotall.fillna(0)
plotall.index = pd.to_datetime(plotall.index)
plotall.plot()

plotall
t = plotall[["ttn_pir_006"]]
t["day"] = t.index.weekday_name
t["hour"] = t.index.hour

heat = t.pivot("day", "hour", "ttn_pir_006").fillna(0)
ax = sns.heatmap(heat)


# -------- TEST FOR WEBSITE
url  = 'http://127.0.0.1:5000/api/table?table=ttn_mot&week=34&filter=1'
data = getdata(url)

url_machine  = 'http://127.0.0.1:5000/api/machines?kind=mot'
machines = getdata(url_machine)

data.time = pd.to_datetime(data["time"])
data.time = data.time + datetime.timedelta(hours = 2)

time_now = str(datetime.datetime.now())
time = str(datetime.datetime.now() - datetime.timedelta(hours = 2))

data = data.set_index("time")
filtered = data[time:time_now]
filtered = filtered.reset_index()
filtered = filtered.drop_duplicates(subset ="dev_id", keep = "last") 
filter_time = filtered.time.max()
devices = machines["dev_id"].unique()


for device in devices:
	if device not in filtered.dev_id.unique():
		newrow = {'time': filter_time, 'dev_id': device, 'value': np.nan}
		filtered = filtered.append(newrow, ignore_index= True)

df =filtered.set_index("dev_id").join(machines.set_index("dev_id")).drop(columns ="time").reset_index()
df.value = df.value.apply(str)

dict_dash_mot = df.to_dict('records')


for i in range(0,len(dict_dash_mot)):
	print(dict_dash_mot[i]["value"])


# °°°°° test 2
week = str(datetime.datetime.now().isocalendar()[1])
url  = 'http://127.0.0.1:5000/api/table?table=ttn_pir&week='+week+'&filter=0'
data = getdata(url)

url_machine  = 'http://127.0.0.1:5000/api/machines?kind=pir'
machines = getdata(url_machine)

dict= {}

for device in range(0,len(machines)):
	df = data.loc[data.dev_id == machines["dev_id"][device]]
	#set index to time and drop this column
	df = df.set_index(pd.to_datetime(df.time)).drop(columns=["time"])
	if( df.empty == True):
		continue

	#get last captured data time
	day = df.index.max()+ datetime.timedelta(hours = 1)
	#Last week day
	start = day - datetime.timedelta(days=day.weekday())
	end = start + datetime.timedelta(days=4)
	end = end.replace(hour = 23)

	#from time to 17 on the friday of the week
	lst = pd.date_range(df.index.max(), end = end, freq='H')
	dct = {'time': lst, 'dev_id':machines["dev_id"][device], 'value': 0}  
	newdf = pd.DataFrame(dct)

	df = df.reset_index().append(newdf).set_index("time")

	df["dayofweek"] = df.index.dayofweek
	df["hour"] = (df.index.hour)


	#filter on hour
	df = df.loc[(df["hour"] > 8 ) & (df["hour"] < 18 )]
	df = df.sort_values(["dayofweek","hour"], ascending = [False,True])
	list_heatmap = df[["hour", 'dayofweek', 'value']].values.tolist()
	dict[machines["machine_name"][device]] = list_heatmap

dict

