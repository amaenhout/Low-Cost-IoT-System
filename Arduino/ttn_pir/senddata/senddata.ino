#include <TheThingsNetwork.h>


// Set your AppEUI and AppKey
const char *appEui = "70B3D57ED001D6E5";
const char *appKey = "CCEAFE2951E0621D3CB9F8AE37A1FE1F";

int led = 13;                // the pin that the LED is atteched to
int red = 11;
int green = 10;
int blue = 9;

int sensor = 2;              // the pin that the sensor is atteched to
int state = LOW;             // by default, no motion detected
int val = 0;                 // variable to store the sensor status (value)
int calibrationTime = 30; // calibration time
int sum = 0;
unsigned long starttime;
unsigned long stoptime;
unsigned long dur;
int duration = 0;



#define ARRAYSIZE 6
int results[ARRAYSIZE] = { 0, 0 , 0 , 0 , 0 , 0 };

#define loraSerial Serial1
#define debugSerial Serial

// Replace REPLACE_ME with TTN_FP_EU868 or TTN_FP_US915
#define freqPlan TTN_FP_EU868 

#define PORT_START 1
#define PORT_STOP 2
#define PORT_SETUP 3


TheThingsNetwork ttn(loraSerial, debugSerial, freqPlan);

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
  
  debugSerial.println("-- SEND: SETUP");
  senddata(PORT_SETUP,duration);
  delay(50);
  
}

void senddata(uint8_t port,int duration)
{
  // Wake RN2483
  ttn.wake();
  debugSerial.println("duration");
  debugSerial.println(duration);

  byte *bytes;
  byte payload[2];

  uint16_t duration_time = duration;
  debugSerial.println(duration_time);
  bytes = (byte *)&duration;
  payload[0] = bytes[1];
  payload[1] = bytes[0];


  ttn.sendBytes(payload, sizeof(payload), port);
  // and say bye bye to RN2983 sleep mode
  delay(50);
}

int checksensor(){
  RGB_color(0, 0, 255);
  val = digitalRead(sensor);   // read sensor value
  int sum = 0;
  for (int i =0; i< ARRAYSIZE; i++) {
    results[i] = 0;
  }
  if (val == HIGH) {  
         digitalWrite(led, HIGH);
              RGB_color(0, 255, 0);
              delay(1000);
              RGB_color(0,0,255);
    } else{
      RGB_color(255, 0, 0);
      delay(1000);
      RGB_color(0,0,255);
    }
    
    results[0] = val; 
    sum = sum + val;
    debugSerial.println("val 0 = "+ String(val));
  
    for (int i =1; i< ARRAYSIZE; i++) {
      delay(10000); //// wait 10 seconds to check next movement
      val = digitalRead(sensor);
      debugSerial.println("val "+String(i)+" = "+val);

      results[i] = val;
      sum = sum + results[i];
      
       if (val == HIGH) {  
         digitalWrite(led, HIGH);
              RGB_color(0, 255, 0);
              delay(1000);
              RGB_color(0,0,255);
    } else{
      RGB_color(255, 0, 0);
      delay(1000);
     RGB_color(0,0,255);
    }
      
    }
    debugSerial.println("sum = " + String(sum));

    if (sum > 3){
       return 1;
    } else{
      return 0;
    }
}


void loop() {
  RGB_color(0,0,100);
  // the pir sensor is on
  if (state == HIGH){
    debugSerial.println("CHECK IF STILL IN USE");
   
    // if the pir sensor is off now -> send stop signal
    if(checksensor() == 0){
      state = LOW;
      RGB_color(0, 0, 0);
      debugSerial.print("----SEND STOP");
      
      stoptime = millis();
      dur = (stoptime - starttime) / 1000;
      debugSerial.println("stop");
      debugSerial.println(starttime);

      debugSerial.println(stoptime);
      debugSerial.println(String(dur));
      
      senddata(PORT_STOP,dur);
      
      for (int i =0; i< ARRAYSIZE; i++) {
        results[i] = 0;
        sum = 0;
      }
    }
     else{
      debugSerial.println("MACHINE STILL IN USE");
     }

    delay(10000); // wait 5 min 

  } else{
    val = digitalRead(sensor);   // read sensor value
    if (val == HIGH) {           // check if the sensor is HIGH
      RGB_color(0, 255, 0);
      delay(1000);
      RGB_color(0,0,0);
      if(checksensor() == 1){
        debugSerial.print("----SEND START");
        if (state == LOW){
          state = HIGH;  
        }  
      dur = 0;
      starttime = millis();
      debugSerial.println("start");
      debugSerial.println(starttime);
      senddata(PORT_START,dur);
      RGB_color(0,255,0);
      delay(10000); // wait 5 min
      
      } else{
        RGB_color(0,0,100);
      }
    } 
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


  
//  debugSerial.println("-- LOOP");
//
//  uint32_t humidity = dht.readHumidity(false) * 100;
//  uint32_t temperature = dht.readTemperature(false) * 100;
//
//  debugSerial.println("Humidity: "+String(humidity));
//  debugSerial.println("Temperature: "+ String(temperature)) ;
//
//  byte payload[4];
//
//  payload[0] = highByte(humidity);
//  payload[1] = lowByte(humidity);
//  payload[2] = highByte(temperature);
//  payload[3] = lowByte(temperature);
//
//  ttn.sendBytes(payload, sizeof(payload));
//
//  delay(600000);
