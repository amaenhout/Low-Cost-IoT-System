# A lambda function to interact with AWS RDS MySQL

import pymysql
import sys
import json

REGION = 'eu-west-2'

rds_host  = "bartlett-workshop.cejtaaej7sbz.eu-west-2.rds.amazonaws.com"
name = "arthur"
password = "Amemvs02#"
db_name = "bartlett_workshop"

def lambda_handler(event, context):
	result = []
	conn = pymysql.connect(rds_host, user=name, passwd=password, db=db_name, connect_timeout=5)

	with conn.cursor() as cur:
		cur.execute("""select * from environmental""")
		conn.commit()
		cur.close()
		for row in cur:
			result.append(list(row))

	return {
		'statusCode': 200,
		'body': json.dumps(result)
	}
