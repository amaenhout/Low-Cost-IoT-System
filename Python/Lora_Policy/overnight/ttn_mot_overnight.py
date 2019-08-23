import ttn

#change app and access key to application
app_id = "bartlett_workshop_motion"
access_key = "ttn-account-v2.z1Bc7J0rVK1FVBwzToDLBh7j7DtLMKUI6NP_ujP4TwI"

# handlerclient class constructor
handler = ttn.HandlerClient(app_id, access_key)
print("Handler initialised")

# using mqtt client create an MQTTClient object
mqtt_client = handler.data()
print("MQTT client object created")

# connect to the application and listen for messages
mqtt_client.connect()

application = handler.application()
json = application.devices()
devices = []

for i in range(0,len(json)):
	devices.append(json[i].dev_id)

#send downlink
payload = {"status":"overnight"}
port = 4
for device in devices:
	mqtt_client.send(device,  payload, port=port, conf=True, sched="replace")

#close mqtt client
mqtt_client.close()


