#include <TheThingsNetwork.h>

// Set your AppEUI and AppKey
const char *appEui = "70B3D57ED001D6E4";
const char *appKey = "F7305D2DAAED1967F25DB8E17267A1F5";

#define loraSerial Serial1
#define debugSerial Serial

// Replace REPLACE_ME with TTN_FP_EU868 or TTN_FP_US915
#define freqPlan TTN_FP_EU868 

TheThingsNetwork ttn(loraSerial, debugSerial, freqPlan);

#define PORT_START 1
#define PORT_STOP 2
#define PORT_SETUP 3


int led = 13;                // the pin that the LED is atteched to
int red = 11;
int green = 10;
int blue = 9;

int sensor = 2;              // the pin that the sensor is atteched to
int state = LOW;             // by default, no motion detected
int val = 0;                 // variable to store the sensor status (value)
int calibrationTime = 30; // calibration time

#define ARRAYSIZE_BIN 8
char Arr_BIN[ARRAYSIZE_BIN] = {'0','0','0','0','0','0','0','0'};

#define ARRAYSIZE_SECS 3
int Arr_SECS[ARRAYSIZE_SECS] = { 0, 0,0};

#define PAYLOAD_SIZE 4

byte var = 0;
long value_1 = 0; // values min 0 - 4
long value_2 = 0; // values min 5 - 8
long value_3 = 0; // values min 9 - 12
long value_4 = 0; // values min 13 - 16

int inter_val = 30; // change time to interval sequence

int position = 0;

int status = 0; // check status (0 = day, 1= overnight -> do not send data)

void setup()
{
  loraSerial.begin(57600);
  debugSerial.begin(9600);
 
  // Wait a maximum of 10s for Serial Monitor
  while (!debugSerial && millis() < 10000)
    ;

  debugSerial.println("-- STATUS");
  ttn.showStatus();

  debugSerial.println("-- JOIN");
  ttn.join(appEui, appKey);

   ttn.onMessage(message);


  pinMode(led, OUTPUT);      // initalize LED as an output
  pinMode(red, OUTPUT);      // initalize LED as an output
  pinMode(green, OUTPUT);      // initalize LED as an output
  pinMode(blue, OUTPUT);      // initalize LED as an output

  pinMode(sensor, INPUT);    // initialize sensor as an input
  //give the sensor some time to calibrate
  
  debugSerial.print("calibrating sensor ");
  for(int i = 0; i < calibrationTime; i++){
    RGB_color(0, 255, 255);
    debugSerial.print(".");
    delay(1000);
    RGB_color(255, 255, 0);
  }
  debugSerial.println(" done");
  debugSerial.println("SENSOR ACTIVE");
  
//  debugSerial.println("-- SEND: SETUP");
//  senddata(PORT_SETUP,duration);
  delay(50);
  
}
void loop() {
  if(status == 0){
    RGB_color(0,0,100);
    debugSerial.println("-- START INTERVAL");
    debugSerial.print("MINUTE: ");
    debugSerial.println(position);
  
    //check if in use for comming seconds: 
    int sum = 0;
    // check sensor
    debugSerial.print("check: ");
    for (int i = 0; i < ARRAYSIZE_SECS; i++){
      //check the value of the sensor
      val = digitalRead(sensor);
      // change the value in the array
      Arr_SECS[i] = val;
      // calculate the sum 
      sum = sum + val;
      debugSerial.print(i);
      debugSerial.print(" = " );
      debugSerial.print( val );
      debugSerial.print(" // " );
      // delay for 10 seconds
      delay(10000); // 10 seconds delay will split each position in 30 seconds
      //debugSerial.print("test1");
    }
    debugSerial.print("test2");
  
    debugSerial.print("sum: ");
    debugSerial.println(sum);
    
    //check if the machine was on these seconds
    if (sum >= 2){
      Arr_BIN[(position) % 8] = '1';
    }
    
    if(((position + 1) % 8) == 0){
      debugSerial.println("ARRAY: ");
      debugSerial.println("01234567");
      for (int i = 0; i < ARRAYSIZE_BIN; i++){
        debugSerial.print(Arr_BIN[i]);
      }
      debugSerial.println(" arr end");
      
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
           sendData(PORT_START,value_1,value_2,value_3,value_4);
           position = 0;
           break;
       }
       // reset array
      for(int i = 0; i < ARRAYSIZE_BIN; i++) {
            Arr_BIN[i] = '0';
      }
    }
    else{
    position ++;
    }
    debugSerial.println("-- END INTERVAL");
  }
}

void RGB_color(int red_light_value, int green_light_value, int blue_light_value)
 {
   red_light_value = 255 - red_light_value;
   green_light_value = 255 - green_light_value;
   blue_light_value = 255 - blue_light_value;
    
  analogWrite(red, red_light_value);
  analogWrite(green, green_light_value);
  analogWrite(blue, blue_light_value);
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
