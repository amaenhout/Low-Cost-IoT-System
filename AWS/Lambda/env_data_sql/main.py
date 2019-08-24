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
    with conn.cursor() as cur:
        cur.execute("""insert into bartlett_workshop.environmental (device_id, time, humidity,temperature) values( '%s', '%s', %s, %s)""" % (event["dev_id"], event["metadata.time"],event["payload_fields.humidity"],event["payload_fields.temperature"]))
        cur.execute("""select * from environmental""")
        conn.commit()
        cur.close()
        for row in cur:
            result.append(list(row))
        print("Data from RDS...")
        print(result)

def main(event, context):
    save_events(event)
