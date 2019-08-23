#include <TheThingsNode.h>

// Set your AppEUI and AppKey
const char *appEui = "70B3D57ED001D5BF";
const char *appKey = "71960AE7D9644AEBE07E9077DCF105D5";

#define loraSerial Serial1
#define debugSerial Serial

// Replace REPLACE_ME with TTN_FP_EU868 or TTN_FP_US915
#define freqPlan TTN_FP_EU868

TheThingsNetwork ttn(loraSerial, debugSerial, freqPlan);
TheThingsNode *node;

#define PORT_SETUP 1
#define PORT_START 2
#define PORT_STOP 3
#define PORT_BUTTON 4

int duration = 0;

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
  node->configInterval(true, 60000);
  node->configTemperature(true);
  node->onWake(wake);
  node->onSleep(sleep);
  node->onMotionStart(onMotionStart);
  node->onMotionStop(onMotionStop);

  // Test sensors and set LED to GREEN if it works
  node->showStatus();
  node->setColor(TTN_GREEN);

  debugSerial.println("-- TTN: STATUS");
  ttn.showStatus();

  debugSerial.println("-- TTN: JOIN");
  ttn.join(appEui, appKey);

  debugSerial.println("-- SEND: SETUP");
  sendData(PORT_SETUP,duration);
}

void loop()
{
  node->loop();
}

void wake()
{
  node->setColor(TTN_GREEN);
}

void sleep()
{
  node->setColor(TTN_BLACK);
}

void onMotionStart()
{
  node->setColor(TTN_BLUE);
  debugSerial.println("-- SEND: MOTION START");
  int dur = 0;
  sendData(PORT_START,dur);
  
}

void onMotionStop(unsigned long duration)
 {
  node->setColor(TTN_BLACK);
  debugSerial.println("-- SEND: MOTION STOP");
  
  int dur = duration / 1000;
  sendData(PORT_STOP,dur);

 }

void sendData(uint8_t port,int duration)
{
  // Wake RN2483
  ttn.wake();

//  ttn.showStatus();
//  node->showStatus();

  byte *bytes;
  byte payload[2];

  uint16_t duration_time = duration;
  bytes = (byte *)&duration_time;
  payload[0] = bytes[1];
  payload[1] = bytes[0];


  ttn.sendBytes(payload, sizeof(payload), port);

  // Set RN2483 to sleep mode
  ttn.sleep(60000);

  // This one is not optionnal, remove it
  // and say bye bye to RN2983 sleep mode
  delay(50);
}
