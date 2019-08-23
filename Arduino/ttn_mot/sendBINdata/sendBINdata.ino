#include <TheThingsNode.h>

// Set your AppEUI and AppKey
const char *appEui = "70B3D57ED001D6E4";
const char *appKey = "A241FDF239E532367E3206D60F478401";


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
#define ARRAY_SIZE 6
int duration = 0;

int Arr_Minute[ARRAY_SIZE];
int minute = 0;


void setup() {
  loraSerial.begin(57600);
  debugSerial.begin(9600);
  // Wait a maximum of 10s for Serial Monitor
  while (!debugSerial && millis() < 10000)
    ;

  // Config Node
  node = TheThingsNode::setup();
  node->configLight(true);
  node->configInterval(true, 1000); // change to 5 min to send the data
  node->onInterval(interval);
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

void interval() {
   debugSerial.println("-- START INTERVAL");
    debugSerial.println(ARRAY_SIZE);

    // loop over minutes
    for(int minute = 0; minute<ARRAY_SIZE; minute++){
       int starttime =  millis();
        int endtime = starttime;
        debugSerial.print("-- START MIN ");
        debugSerial.println(minute);
        while ((endtime - starttime) <= 5000){ // do this loop for up to 5S 
            endtime = millis();
        }        
        
            debugSerial.println("-- ARRAY END ");
     }
    debugSerial.println("-- END ARRAY : ");
    for(int i = 0; i < ARRAY_SIZE; i++) {
        debugSerial.print(Arr_Minute[i]);
    }
    debugSerial.println("-- END");
    minute = 0;
    // reset array
    for(int i = 0; i < ARRAY_SIZE; i++) {
        Arr_Minute[i] = 0;
    }
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
  debugSerial.println("-- SET: MOTION ON");

  Arr_Minute[minute] = 1;
    
}

void onMotionStop(unsigned long duration)
 {
  node->setColor(TTN_BLACK);
  debugSerial.println("-- SEND: MOTION STOP");
  
  int dur = duration / 1000;
  //sendData(PORT_STOP,dur);

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
