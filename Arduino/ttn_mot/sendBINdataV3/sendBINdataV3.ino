#include <TheThingsNode.h>

// Set your AppEUI and AppKey
const char *appEui = "70B3D57ED001D6E4";
const char *appKey = "F7305D2DAAED1967F25DB8E17267A1F5";


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


#define ARRAY_SIZE 8 // array

#define PAYLOAD_SIZE 4 // payload to send data to ttn

int status = 0; // check status (0 = day, 1= overnight -> do not send data)


int duration = 0;

char Arr_BIN[ARRAY_SIZE] = {'0','0','0','0','0','0','0','0'};

int position = 0; // position in the array (0-4)

int on = 0; // machine on time
int off = 0; // machine off time
byte var = 0;
long value_1 = 0; // values min 0 - 4
long value_2 = 0; // values min 5 - 8
long value_3 = 0; // values min 9 - 12
long value_4 = 0; // values min 13 - 16

bool motion_on = false;
bool motion_on_pos = false; 

int inter_val = 30; // change time to interval sequence


void setup() {
  loraSerial.begin(57600);
  debugSerial.begin(9600);
  // Wait a maximum of 10s for Serial Monitor
  while (!debugSerial && millis() < 10000)
    ;

  // Config Node
  node = TheThingsNode::setup();
  node->configLight(true);
  node->configInterval(true, (inter_val*1000)); // change to 30s to send the data
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

  ttn.onMessage(message);
//  debugSerial.println("-- SEND: SETUP");
//  sendData(PORT_SETUP,0,0,0,0);
}

void loop()
{
  node->loop();
 
}
void interval() {
  if(status == 0){
    debugSerial.println("day");
  
    debugSerial.println("-- START INTERVAL");
    debugSerial.print("MINUTE: ");
    debugSerial.println(position);
    
    // check if the start minute is the same as the stopped one
    if (motion_on == true){ // pos is the same -> same minute -> on off comparsison
        Arr_BIN[(position) % 8] = '1'; // we need to take the modulus of the position -> minute to 31
     } else if (motion_on_pos == true){ // pos is the same -> same minute -> on off comparsison
        Arr_BIN[(position) % 8] = '1'; // we need to take the modulus of the position -> minute to 31
     } else {
        Arr_BIN[(position) % 8] = '0'; // we need to take the modulus of the position -> minute to 31
     }
    // if mod of position 8 is 0 -> do something
    if(((position + 1) % 8)  == 0){
       // save array
       char str_arr[9];
       str_arr[8] = '\0';
       memcpy(str_arr, Arr_BIN, 8);
       debugSerial.println(str_arr);
       switch (position + 1) {
           case 8: //do something when position equals 8
            value_1 = strtol(str_arr, NULL, 2);
            position++;
            break;
          case 16: //do something when position equals 16
            value_2 = strtol(str_arr, NULL, 2);
            position++;
            break;
          case 24: //do something when position equals 24
            value_3 = strtol(str_arr, NULL, 2);
            position++;
            break;
          case 32: //do something when position equals 32
            value_4 = strtol(str_arr, NULL, 2);
  
            // send the data
            debugSerial.println("--SEND DATA");
            sendData(PORT_START,value_1,value_2,value_3,value_4);
            position = 0;
            break;            
        }    
      // reset array
      for(int i = 0; i < ARRAY_SIZE; i++) {
          Arr_BIN[i] = '0';
      }
    }
    // if not set the value of the minute within the array
    else{
    // set minute to next one
     position++;
     motion_on = false;
   }
  debugSerial.println("-- END INTERVAL");
  } // end status
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
  motion_on = true;
  motion_on_pos = true;
}

void onMotionStop(unsigned long duration)
 {
  node->setColor(TTN_BLACK);
  debugSerial.println("-- SEND: MOTION STOP");
  motion_on_pos = false;
 }

void sendData(uint8_t port,long value_1,long value_2,long value_3,long value_4)
{
  // Wake RN2483
  ttn.wake();
  debugSerial.println("-- SEND DATA");

  byte payload[PAYLOAD_SIZE];

  payload[0] = value_1;
  payload[1] = value_2;
  payload[2] = value_3;
  payload[3] = value_4;
  
  

  ttn.sendBytes(payload, sizeof(payload), port);

  // Set RN2483 to sleep mode
  ttn.sleep(60000);

 
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
