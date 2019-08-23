#include <TheThingsNode.h>

// Set your AppEUI and AppKey
const char *appEui = "70B3D57ED001D5BF";
const char *appKey = "938C1B4D8B1A6F99E9110DF4C26AD710";

#define loraSerial Serial1
#define debugSerial Serial

// Replace REPLACE_ME with TTN_FP_EU868 or TTN_FP_US915
#define freqPlan TTN_FP_EU868

TheThingsNetwork ttn(loraSerial, debugSerial, freqPlan);
TheThingsNode *node;

#define PORT_SETUP 1
#define PORT_INTERVAL 2
#define PORT_MOTION 3
#define PORT_BUTTON 4

int status = 0; // check status (0 = day, 1= overnight -> do not send data)

//delay for about 14 hours -> from 18PM until 8AM to save battery power + delay messages
// 50400 seconds
// 50400000000000000 micro seconds
// 
const unsigned long inter_val = 900000UL; //900000
//const int inter_val = 5000;
//const unsigned long overnight_delay = 1000*3600*14UL;
//const unsigned long weekend_delay = 1000*3600*62UL;


void setup()
{
  loraSerial.begin(57600);
  debugSerial.begin(9600);

  // Wait a maximum of 10s for Serial Monitor
  while (!debugSerial && millis() < 10000)
    ;

  // Config Node
  node = TheThingsNode::setup();
  node->configLight(true);
  node->configInterval(true, inter_val);
  node->configTemperature(true);
  node->onWake(wake);
  node->onInterval(interval);
  node->onSleep(sleep);
  

  // Test sensors and set LED to GREEN if it works
  node->showStatus();
  node->setColor(TTN_GREEN);

  debugSerial.println("-- TTN: STATUS");
  ttn.showStatus();

  debugSerial.println("-- TTN: JOIN");
  ttn.join(appEui, appKey);
  
  ttn.onMessage(message);
  
  
  debugSerial.println("-- SEND: SETUP");
  sendData(PORT_SETUP);

  debugSerial.println("-- TIME INTERVAL");
  debugSerial.println( inter_val );
}

void loop()
{
  node->loop();
}

void interval()
{
  node->setColor(TTN_BLUE);
  debugSerial.println("-- SEND: INTERVAL");
  debugSerial.println(status);

  sendData(PORT_INTERVAL);
 // if(status == 0){
 //   debugSerial.println("day");
 //   sendData(PORT_INTERVAL);
 // }
}

void wake()
{
  node->setColor(TTN_GREEN);
}

void sleep()
{
  node->setColor(TTN_BLACK);
}
void sendData(uint8_t port)
{
  // Wake RN2483
  ttn.wake();

  ttn.showStatus();
  node->showStatus();

  byte *bytes;
  byte payload[6];

  uint16_t battery = node->getBattery();
  bytes = (byte *)&battery;
  payload[0] = bytes[1];
  payload[1] = bytes[0];

  uint16_t light = node->getLight();
  bytes = (byte *)&light;
  payload[2] = bytes[1];
  payload[3] = bytes[0];

  int16_t temperature = round(node->getTemperatureAsFloat() * 100);
  bytes = (byte *)&temperature;
  payload[4] = bytes[1];
  payload[5] = bytes[0];

  ttn.sendBytes(payload, sizeof(payload), port);

  // Set RN2483 to sleep mode
  ttn.sleep(60000);

  // This one is not optionnal, remove it
  // and say bye bye to RN2983 sleep mode
  delay(50);
}
void message(const uint8_t *payload, size_t size, port_t port){
   
   if (payload[0] == 0){ // day
    status= 0;
    debugSerial.println("day");
   } else if (payload[0] == 1){ // overnight
    status= 1;
    debugSerial.println("overnight");
   }
   debugSerial.println(status);
  
}
