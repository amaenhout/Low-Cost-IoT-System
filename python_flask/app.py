from flask import Flask, render_template, jsonify,request,Response
import pymysql
import datetime as datetime
import pandas as pd
import requests
import numpy as np
from pandas.io.json import json_normalize

date_fmt = "%Y-%m-%d  %H:%M:%S %Z%z"
app = Flask(__name__,static_url_path='', static_folder='web/static', template_folder='web/templates')

def getdata(url):
	res = requests.get(url)
	data = res.json()

	df_api = json_normalize(data)
	return df_api


def return_week(row):
	if (row == 0):
		return 4
	elif (row == 1):
		return 3
	elif (row == 2):
		return 2
	elif (row == 3):
		return 1
	elif (row == 4):
		return 0

def get_chart_1(data,kind):
	df = data[["dev_id",kind]]

	data_df = df.groupby("dev_id").resample('H').mean().unstack("dev_id").fillna(method="ffill").reset_index()
	data_df = data_df.set_index("time")

	series = [{ 'name': key,'data': list(value.values),} for key, value in data_df.items()]

	dates = pd.DataFrame(data_df.index)
	dates = list(pd.to_timedelta(dates.time).dt.total_seconds().astype(int))
	return series,dates

def getheatmap(data,machines):
	dict = {}
	getdate_df = data.set_index(pd.to_datetime(data.time)).drop(columns=["time"])
	date = getdate_df.index.max()+ datetime.timedelta(hours = 1)
	for device in range(0,len(machines)):
		df = data.loc[data.dev_id == machines["dev_id"][device]]
		#set index to time and drop this column
		df = df.set_index(pd.to_datetime(df.time)).drop(columns=["time"])
		if( df.empty == True):
			continue

		#get last captured data time
		min_day = df.index.min()+ datetime.timedelta(hours = 1)
		max_day = df.index.max()+ datetime.timedelta(hours = 1)

		#Last week day
		start = max_day - datetime.timedelta(days=max_day.weekday())
		end = start + datetime.timedelta(days=4)
		end = end.replace(hour = 23)
		start = start.replace(hour = 9)

		if (start != min_day):
			#create dataframe from start of the week until the minday minus one hour
			lst = pd.date_range(start = start,end = df.index.min()- datetime.timedelta(hours = 1), freq='H')
			dct = {'time': lst, 'dev_id':machines["dev_id"][device], 'value': 0}  
			first_df = pd.DataFrame(dct)
			dataset = first_df.append(df.reset_index()).set_index("time")


		if (end != max_day):
			#from time to 17 on the friday of the week
			lst = pd.date_range(df.index.max()+ datetime.timedelta(hours = 1), end = end, freq='H')
			dct = {'time': lst, 'dev_id':machines["dev_id"][device], 'value': 0}  
			second_df = pd.DataFrame(dct)
			dataset = dataset.reset_index().append(second_df).set_index("time")

		dataset["dayofweek"] = dataset.index.dayofweek
		dataset["new_dayofweek"] = dataset["dayofweek"].apply(return_week)
		dataset["hour"] = (dataset.index.hour)

		
		#filter on hour
		dataset = dataset.loc[(dataset["hour"] > 8 ) & (dataset["hour"] < 18 )]
		dataset = dataset.sort_values(["new_dayofweek","hour"], ascending = [False,True])
		list_heatmap = dataset[["hour", 'new_dayofweek', 'value']].values.tolist()
		dict[machines["machine_name"][device]] = list_heatmap
	return dict,date


class Database:
	def __init__(self):
		host = "bartlett-workshop.cejtaaej7sbz.eu-west-2.rds.amazonaws.com"
		user = "user"
		password = "user123"
		db = "bartlett_workshop"
		self.con = pymysql.connect(host=host, user=user, password=password, db=db, cursorclass=pymysql.cursors.
								   DictCursor,port = 3306)
		self.cur = self.con.cursor()

	def list_table(self,tablename,weeknum):
		self.cur.execute("SELECT * FROM "+tablename + " WHERE week(time,1) = "+weeknum)
		result = self.cur.fetchall()
		return result
	
	def list_table_dates(self,tablename,start,end):
		#select * from ttn_env where date(time) >= "2019-07-22";
		startdt = str(datetime.datetime.strptime(start, date_fmt).date())

		if (end == 0):
			self.cur.execute("SELECT * FROM  ttn_env WHERE date(time) > "+startdt)
			result = self.cur.fetchall()
			return result
		else: 
			enddt = str(datetime.datetime.strptime(end, date_fmt).date())
			self.cur.execute("SELECT * FROM "+tablename+ " WHERE date(time) >= "+startdt+" and time =< "+enddt)
			result = self.cur.fetchall()
			return result
			
	def list_realtime_env(self):
		self.cur.execute("select l.dev_id,l.time,l.temperature,l.light from ttn_env as l JOIN (select dev_id,max(time) as time from ttn_env GROUP BY dev_id) as r ON r.dev_id = l.dev_id and r.time = l.time")
		result = self.cur.fetchall()
		return result
	
	def list_realtime_mot(self):
		self.cur.execute("select * from ttn_machine_status where dev_id LIKE '%mot%'")
		result = self.cur.fetchall()
		return result

	def list_realtime_pir(self):
		self.cur.execute("select * from ttn_machine_status where dev_id LIKE '%pir%'")
		result = self.cur.fetchall()
		return result

	def list_machines(self,kind):
		self.cur.execute("select s.dev_id,i.machine_name from ttn_machine_status s inner join ttn_machine_info i on s.dev_id = i.dev_id where i.dev_id like '%"+kind+"%'")
		result = self.cur.fetchall()
		return result



def resample_df_to_json(query,freq,table,filter):
	#result to dataframe
	df = pd.DataFrame(query)
	#set index to time and drop this column
	df = df.set_index(pd.to_datetime(df.time),drop=True).drop(columns=["id","time"])
	#group by dev_id, resample for every 15 min and fill in na with last know value, reset indexes
	
	
	if (table == "ttn_env"):
		data = df.groupby('dev_id').resample(freq).mean().reset_index()
	elif(table == "ttn_mot"):
		data = df.groupby('dev_id').resample(freq).sum().reset_index()
		data["value"] = data["value"] / 2
	elif(table == "ttn_pir"):
		data = df.groupby('dev_id').resample(freq).sum().reset_index()
		data["value"] = data["value"] / 2
	#print(filter)
	if (filter == "1"):
		#filter on hour
		data["hour"] = (data["time"].dt.hour)
		data = data.loc[(data["hour"] > 8 ) & (data["hour"] < 18 )]
		data = data.drop(columns = "hour")

		#filter on weekday
		data["weekday"] = (data["time"].dt.weekday_name)
		#print(data.head())
		data = data.loc[(data["weekday"] != "saturday" ) & (data["weekday"] != "sunday" )]
		data = data.drop(columns = "weekday")
	
	#sort values by the time
	sort_df = data.sort_values("time")
	
	resp = Response(response=sort_df.to_json(orient='records',date_format='iso', date_unit='s'),status=200,mimetype="application/json")
	return resp



#####################################################################
###########################PAGES#####################################
#####################################################################

@app.route('/api_docu') # index table for API
def api_docu():
	return render_template("api_docu.html")

@app.route('/index') # index table for API
def index():
	return render_template("index.html")

@app.route('/dashboard') # index table for API
def dashboard():
	#get realtime information for dashboard
	def db_query_env():
		db = Database()
		table_dates = db.list_realtime_env()
		return table_dates
	env = pd.DataFrame(db_query_env())
	
	def db_query_mot():
		db = Database()
		table_dates = db.list_realtime_mot()
		return table_dates

	mot = pd.DataFrame(db_query_mot())
	
	
	def db_query_pir():
		db = Database()
		table_dates = db.list_realtime_pir()
		return table_dates
	pir = pd.DataFrame(db_query_pir())
	
	thisdict =	{
		"temp": round(env["temperature"].mean(),2),
		"light": round(env["light"].mean(),2),
		"mot":  mot["status"].sum(),
		"mot_count":mot["status"].count(),
		"pir": pir["status"].sum(),
		"pir_count":pir["status"].count()
	}
	
	#get MOTION
	url  = 'http://127.0.0.1:5000/api/table?table=ttn_mot&week=34&filter=1'
	data = getdata(url)

	url_machine  = 'http://127.0.0.1:5000/api/machines?kind=mot'
	machines = getdata(url_machine)

	data.time = pd.to_datetime(data["time"])
	data.time = data.time + datetime.timedelta(hours = 1)

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
			newrow = {'time': filter_time, 'dev_id': device, 'value': "no data"}
			filtered = filtered.append(newrow, ignore_index= True)

	df =filtered.set_index("dev_id").join(machines.set_index("dev_id")).drop(columns ="time").reset_index()
	df.value = df.value.apply(str)
	df = df.sort_values("machine_name")

	dict_dash_mot = df.to_dict('records')

	#get PIR
	url  = 'http://127.0.0.1:5000/api/table?table=ttn_pir&week=34&filter=1'
	data = getdata(url)

	url_machine  = 'http://127.0.0.1:5000/api/machines?kind=pir'
	machines = getdata(url_machine)

	data.time = pd.to_datetime(data["time"])
	data.time = data.time + datetime.timedelta(hours = 1)
	
	time_now = str(datetime.datetime.now())
	time = str(datetime.datetime.now() - datetime.timedelta(hours = 2))
	# check if after 17h otherwise -> 17 o'clock
	data = data.set_index("time")
	filtered = data[time:time_now]
	filtered = filtered.reset_index()
	filtered = filtered.drop_duplicates(subset ="dev_id", keep = "last") 
	
	filter_time_pir = filtered.time.max()
	devices = machines["dev_id"].unique()

	for device in devices:
		if device not in filtered.dev_id.unique():
			newrow = {'time': filter_time, 'dev_id': device, 'value': "no data"}
			filtered = filtered.append(newrow, ignore_index= True)

	df =filtered.set_index("dev_id").join(machines.set_index("dev_id")).drop(columns ="time").reset_index()
	df.value = df.value.apply(str)
	df = df.sort_values("machine_name")

	dict_dash_pir = df.to_dict('records')

	return render_template("dashboard.html",dict = thisdict,dict_mot = dict_dash_mot,len_mot = len(dict_dash_mot),time_mot = filter_time,dict_pir = dict_dash_pir,len_pir = len(dict_dash_pir),time_pir = filter_time_pir)


@app.route('/environmental') # index table for API
def environmental():
	# ---- CHART 1 
	url  = 'http://127.0.0.1:5000/api/table?table=ttn_env&week=34&filter=0'
	data = getdata(url)

	df = data.set_index(pd.to_datetime(data.time)).drop(columns="time")
	max_day = df.index.max()+ datetime.timedelta(hours = 1)
	
	temp_series,temp_dates = get_chart_1(df,"temperature")
	light_series,light_dates = get_chart_1(df,"light")

	
	return render_template("environmental.html", temp_series=temp_series,temp_dates = temp_dates, light_series=light_series,light_dates =  light_dates,date = max_day)


@app.route('/motion') # index table for API
def motion():
	# ---- CHART 2
	week = str(datetime.datetime.now().isocalendar()[1])
	url  = 'http://127.0.0.1:5000/api/table?table=ttn_mot&week='+week+'&filter=0'
	data = getdata(url)

	url_machine  = 'http://127.0.0.1:5000/api/machines?kind=mot'
	machines = getdata(url_machine).sort_values("machine_name")

	dict,date= getheatmap(data,machines)
	
	return render_template("motion.html",dict = dict,date = date)


@app.route('/pir') # index table for API
def pir():
	# ---- CHART 2
	week = str(datetime.datetime.now().isocalendar()[1])
	url  = 'http://127.0.0.1:5000/api/table?table=ttn_pir&week='+week+'&filter=0'
	data = getdata(url)

	url_machine  = 'http://127.0.0.1:5000/api/machines?kind=pir'
	machines = getdata(url_machine).sort_values("machine_name")

	dict,date= getheatmap(data,machines)
	
	return render_template("pir.html",dict = dict,date = date)

###########################################################################
#################################API#######################################
###########################################################################

@app.route('/api/table') # variables table
def table():
	if ('table' in request.args) and ('week' in request.args) and ('filter' in request.args):
		table = request.args['table']
		weeknum = str(request.args['week'])
		filter = str(request.args['filter'])

	def db_query(tablename,weeknum):
		#weeknum = str(datetime.date.today().isocalendar()[1])
		db = Database()
		table_select = db.list_table(tablename,weeknum)
		return table_select

	if(table == "ttn_env"):
		return resample_df_to_json(db_query(table,weeknum),"1H",table,filter)
	elif (table == "ttn_mot"):
		return resample_df_to_json(db_query(table,weeknum),"1H",table,filter)
	elif (table == "ttn_pir"):
		return resample_df_to_json(db_query(table,weeknum),"1H",table,filter)

	else:
		return "Error: No table field provided. Please specify an table."
		
	

	#return jsonify(db_query(table))

@app.route('/api/realtime') # realtime data
def realtime():
	if 'table' in request.args:
		kind = request.args["table"]
	else:
		return "Error in parameters"

	if (kind == "ttn_env"):
		def db_query():
			db = Database()
			table_dates = db.list_realtime_env()
			return table_dates
	elif(kind == "ttn_mot"):
		def db_query():
			db = Database()
			table_dates = db.list_realtime_mot()
			return table_dates
	elif(kind == "ttn_pir"):
		def db_query():
			db = Database()
			table_dates = db.list_realtime_pir()
			return table_dates
	else:
		return "Error in "
	return jsonify(db_query())


@app.route('/api/machines')
def machines():
	if 'kind' in request.args:
		kind = request.args["kind"]
	def db_query(kind):
		db = Database()
		machines = db.list_machines(kind)
		return machines
	
	return jsonify(db_query(kind))