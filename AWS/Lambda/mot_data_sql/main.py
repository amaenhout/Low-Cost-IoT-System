# A lambda function to interact with AWS RDS MySQL

import pymysql
import sys

REGION = 'eu-west-2'

rds_host  = "bartlett-workshop.cejtaaej7sbz.eu-west-2.rds.amazonaws.com"
name = "arthur"
password = "Amemvs02#"
db_name = "bartlett_workshop"

def save_events(event):
    result = []
    conn = pymysql.connect(rds_host, user=name, passwd=password, db=db_name, connect_timeout=5)
    device_id = event["dev_id"]
    duration = int(event["duration"]) / 1000
    time = event["time"]
    event = event["event"]
    
    print(time)
    print(duration)
    print(time - duration)
    
    if (event == "start"):
        with conn.cursor() as cur:
            # update table to on
            cur.execute("""UPDATE bartlett_workshop.machines SET status = 1 WHERE device_id = '%s' """ % (device_id))
            conn.commit()
            cur.close()

    if (event == "stop"):
        with conn.cursor() as cur:
            # update machines table to off
            cur.execute("""UPDATE bartlett_workshop.machines SET status = 0 WHERE device_id = '%s' """ % (device_id))
            # insert into pir table   
            #cur.execute("""UPDATE bartlett_workshop.machines SET status = 0 WHERE device_id = '%s' """ % (device_id))

            conn.commit()
            cur.close()

def main(event, context):
    save_events(event)
