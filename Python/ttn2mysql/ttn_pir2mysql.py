import time
import ttn
import pymysql
import mysql.connector
from dateutil.parser import parse
from datetime import datetime,timedelta
import iso8601
from pytz import timezone
import pandas as pd
from sqlalchemy import create_engine


#change app and access key to application
app_id = "bartlett_workshop_pir"
access_key = "ttn-account-v2.labLSUQjwJYMoDuZhL2v8kDVu4ICI4CAlN1N7D_KxdQ"



#date format
fmt = "%Y-%m-%d  %H:%M:%S %Z%z"

def uplink_callback(msg, client):
    print("Received uplink from: ")
    print(msg.dev_id)
    print(msg.app_id)
    print(msg.payload_fields)
    print(msg.metadata.time)
    if(msg.payload_fields.event == "interval"):
        #states from ttn
        list_1 = [int(x) for x in list('{0:08b}'.format(msg.payload_fields.min1))]
        list_2 = [int(x) for x in list('{0:08b}'.format(msg.payload_fields.min2))]
        list_3 = [int(x) for x in list('{0:08b}'.format(msg.payload_fields.min3))]
        list_4 = [int(x) for x in list('{0:08b}'.format(msg.payload_fields.min4))]
        
        print list_1
        print list_2
        print list_3
        print list_4
        
        #end date -> subtract 16 min to know the start time
        end = iso8601.parse_date(msg.metadata.time).astimezone(timezone('Europe/London'))
        start = (end - timedelta(minutes=16))
        
        
        #variables
        device_id = msg.dev_id
        #current state:
        current_state = list_4[-1]
        times = pd.Series(pd.date_range(start = start, periods = 32, freq = '30s')).dt.round("30s")
        values = list_1 + list_2 + list_3 + list_4
        df = pd.DataFrame({'dev_id':device_id,'time':times,'value':values})
        
        def rtnStr(row):
            return str(row)
        df["time"] = df["time"].apply(rtnStr)

        engine = create_engine('mysql+pymysql://ttn:Amemvs02@localhost:3306/bartlett_workshop')
        print "engine created"
        
        #push to local server
        try:
            df.to_sql("ttn_pir",con = engine, if_exists = 'append', index = False)
            print("Data in sql")
        except pymysql.InternalError as error :
            code,message = error.args
            print(">>>>>>>>>", code, message)
        
        #database
        rds_host = "localhost"
        name ="ttn"
        password ="Amemvs02"
        db_name="bartlett_workshop"

        conn = pymysql.connect(rds_host,user = name, passwd = password, db = db_name,connect_timeout = 5)

        with conn.cursor() as cur:
            #check if machine is already in database
            cur.execute("""SELECT * FROM ttn_machines_status where dev_id  = ('%s')""" % str(device_id))
            conn.commit()
            result = cur.fetchone()
        
            #if not add machine
            if(result is None):
                cur.execute("""INSERT INTO ttn_machines_status (dev_id,status) VALUES ('%s','%s')""" % (str(device_id),str(0)))
                conn.commit()
              
            #update the current state
            cur.execute("""UPDATE ttn_machines_status set status = '%s' where dev_id  = ('%s')""" % (str(current_state),str(device_id)))
            conn.commit()
            cur.close()
          
        #push to amazon------------------------
        #connect to rds amazon
        rds_host = "bartlett-workshop.cejtaaej7sbz.eu-west-2.rds.amazonaws.com"
        name ="arthur"
        password ="Amemvs02#"
        db_name="bartlett_workshop"
        
        engine = create_engine('mysql+pymysql://arthur:Amemvs02#@bartlett-workshop.cejtaaej7sbz.eu-west-2.rds.amazonaws.com:3306/bartlett_workshop?charset=utf8mb4')
        
        #push to local server
        try:
            df.to_sql("ttn_pir",con = engine, if_exists = 'append', index = False)
            print("Data in sql")
        except pymysql.InternalError as error :
            code,message = error.args
            print(">>>>>>>>>", code, message)
        
        conn = pymysql.connect(rds_host,user = name, passwd = password, db = db_name,connect_timeout = 5, charset= 'utf8')

        with conn.cursor() as cur:
            #check if machine is already in database
            cur.execute("""SELECT * FROM ttn_machine_status where dev_id  = ('%s')""" % str(device_id))
            conn.commit()
            result = cur.fetchone()
          
            #if not add machine
            if(result is None):
                cur.execute("""INSERT INTO ttn_machine_status (dev_id,status) VALUES ('%s','%s')""" % (str(device_id),str(0)))
                conn.commit()
              
            #update the current state
            cur.execute("""UPDATE ttn_machine_status set status = '%s' where dev_id  = ('%s')""" % (str(current_state),str(device_id)))
            conn.commit()
            cur.close()
        

def connect_callback(res, client):
  print "Connection to broker: "
  print res

def close_callback(res, client):
  print "Trying to reconnect"
  mqtt_client.connect()

# handlerclient class constructor
handler = ttn.HandlerClient(app_id, access_key)
print "Handler initialised"

# using mqtt client create an MQTTClient object
mqtt_client = handler.data()
print "MQTT client object created"

# set a connection callback function when client connects to broker
mqtt_client.set_connect_callback(connect_callback)

# set close_callback so that if connection lost we can reconect
mqtt_client.set_close_callback(close_callback)

# set uplink callback to be executed when message arrives
mqtt_client.set_uplink_callback(uplink_callback)
print "Callbacks assigned"

# connect to the application and listen for messages
mqtt_client.connect()

# keep program running - if connection lost should reconnect
while True:
  pass

