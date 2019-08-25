# Master Disseration Arthur Maenhout
Our world is becoming overwhelmed by billions of internet-connected devices, an evolution that will grow even more in the upcoming years. By 2020, 50 billion Internet of Things (IoT) objects will connect to the Internet and each other. With this upcoming trend, new technologies are emerging this on hardware, software and communication sides. This dissertation researches what open source technologies are available to develop an IoT system architecture that is inexpensive yet reliable. Besides, this system is implemented within a workshop to investigate if based on the gathered data it can optimise the space usage. Numerous IoT projects have been conducted in all sectors, this by companies and individuals they use either expensive complete IoT systems or developing new systems that are built for a particular project. I argue that we need to combine the knowledge that is developed in new open source technologies with Industry 4.0 devices and spaces to create an overall working system. Based on the literature review and trial and error, a low-cost IoT system architecture is developed. As the system architecture was successfully developed, it got implemented within the workshop. Analysis of the captured data demonstrated that the system was working as it was hoped for. On this basis, this system can be replicated in both industry IoT projects as individual projects. Further research will be needed to identify the optimal sensors to track space usage and so be able to optimise this usage

## Getting Started
These instructions will get you a copy of the project up and running using The Things Network microcontrollers and gateway, a Raspberry Pi and a cloud AWS database

### Prerequisites
The things you will need to buy and install inorder to make use of the system are:

1. Get a Things Network microcontroller:
    * [Node](https://www.thethingsnetwork.org/docs/devices/node/)
    * [Uno](https://www.thethingsnetwork.org/docs/devices/uno/)
2. Look if there is an LoRaWAN Gateway nearby -> website
    * [Gateway's]()
3. Get a Raspberry Pi Model 3+ B
    * [Raspberry Pi]()
4. Install Arduino IDE
    * [Arduino]()
5. Create an account on AWS
    * [AWS Free Tier]()


### Installing 
The next thing in this project is to install the different hardware and software. 

#### Arduino
The first software that is needed in this projects is the Arduino IDE. This sopen source software makes it possible to control the microcontrollers. To make use of the Things network licrocontrollers, the library needs to be installed: 

#### Microcontrollers
After, in the Arduino folder, the are three different applications:

the environmental application which captures the most basic information the node can give; temperature, light level and the battery level of the node. 

The Motion application,

The PIR application,
#### Raspberry Pi
##### configuration
````bash
sudo raspi−config
````
##### remote it
````bash
sudo apt−get install connectd
sudo connectd installer
````

##### Mariadb
````bash
sudo apt−get install mysql−server 
sudo mysql secure installation
sudo mysql −u root−p
````

##### Crontab
````bash
crontab -e
````
#### AWS
After creating the free tier account on AWS one can start to use the Relational Database services. 
Installment: 


## Python - Files



## Python Flask Web App
When downloading the python flask folder on your local machine

Dashboard: 
![alt text](Images/Website/webpage_dashboard.png "Dashboard")

Graphs - Environmental: 
![alt text](Images/Website/webpage_env.png "Dashboard")

Graphs - Motion: 
![alt text](Images/Website/webpage_mot.png "Dashboard")

Graphs - Pir: 
![alt text](Images/Website/webpage_pir.png "Dashboard")
