import time
import ttn
import pymysql
from dateutil.parser import parse
import iso8601
from pytz import timezone

#ttn
app_id = "bartlett_workshop_environmental"
access_key = "ttn-account-v2.NzzcjEpi3XrT84qV1LmQRJgxPED3H5qIRix8ET5ASAU"

#date format
fmt = "%Y-%m-%d  %H:%M:%S %Z%z"

def uplink_callback(msg, client):
  print "Received uplink from: "
  print msg.dev_id
  print msg.app_id
  print msg.payload_fields
  print msg.metadata.time

  dt = iso8601.parse_date(msg.metadata.time).astimezone(timezone('Europe/London'))
  dt = dt.strftime(fmt)
    
  print dt
  device_id = msg.dev_id
  temperature = msg.payload_fields.temperature
  battery = msg.payload_fields.battery
  light = msg.payload_fields.light
  #connect to local server 
  try:
      #database
      rds_host = "localhost"
      name ="ttn"
      password ="Amemvs02"
      db_name="bartlett_workshop"
      conn = pymysql.connect(rds_host,user = name, passwd = password, db = db_name,connect_timeout = 5)
      
      with conn.cursor() as cur:
          cur.execute("""INSERT INTO ttn_env (dev_id,temperature,light, battery, time) VALUES ('%s', '%s', '%s','%s','%s')""" % (str(device_id), str(temperature),str(light),str(battery), str(dt)))
          conn.commit()
    
      cur.close()
  except pymysql.InternalError as error :
    code,message = error.args
    print ">>>>>>>>>", code, message
        
  #connect to rds amazon
  rds_host = "bartlett-workshop.cejtaaej7sbz.eu-west-2.rds.amazonaws.com"
  name ="arthur"
  password ="Amemvs02#"
  db_name="bartlett_workshop"
  
  try:
      
      print "connect"
      conn = pymysql.connect(rds_host,user = name, passwd = password, db = db_name,connect_timeout = 5)
      
      
      print "execute"
      with conn.cursor() as cur:
          cur.execute("""INSERT INTO ttn_env (dev_id,temperature,light, battery, time) VALUES ('%s', '%s', '%s','%s','%s')""" % (str(device_id), str(temperature),str(light),str(battery), str(dt)))
          conn.commit()
    
      cur.close()
  except pymysql.InternalError as error :
    code,message = error.args
    print ">>>>>>>>>", code, message

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
