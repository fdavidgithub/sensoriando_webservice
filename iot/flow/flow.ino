/* Read flow sensor and publish in MQTT server
 * Francis David (www.fdavid.com.br) 
 * 
 * Build with IDE Arduino 1.8.4
 *
 * SCHEME LED RGB
 * GPIO      Function    On
 * 1        Green       GPIO
 * 2        Ground      GND           
 * 3        Blue        GPIO
 * 4        Red         GPIO
 * 
 * SCHEME FLOW SENSOR
 * GPIO      Function    On
 * Red      VCC         5v
 * Brown    Ground      GND           
 * Yellow   Signal      GPIO
 *
 * SCHEME PUSH BUTTON
 * GPIO      Function    On
 * 1                    GPIO
 * 2              GND           
 * 3              GPIO
 * 4              GPIO
 *
 * REQUIREMENT
 *  Board NodeMCU
 *  Tools>>Board (NodeMCU 1.0)
 *  
 *  Libraries (Sketch >> Include Library >> Manage Libraies)
 *      PubSubClient (MQTT Client)  
 *      WifiManager (Wifi ESSID)
 *      
 *  Server MQTT
 */
#include <ESP8266WiFi.h>    
#include <PubSubClient.h>
#include <DNSServer.h>
#include <ESP8266WebServer.h>
#include <WiFiManager.h>  

#define DEBUG

#define GPIO_RESET   16
#define GPIO_RED     15      //Only GPIO with support PWM
#define GPIO_GREEN   12      //Only GPIO with support PWM
#define GPIO_BLUE    13      //Only GPIO with support PWM    
#define GPIO_SENSOR  2       //Can use all GPIO, except GPIO 16

#define UPD_SENSOR  1000    //Update server in miliseconds
#define DEBOUNCE    1000
#define ELAPSEDTIME 5000

#define MQTT_SERVER "200.159.88.174"
#define MQTT_PORT   1883
#define MQTT_TOPIC  "geral/esp"

#define LITERS(PULSE)   (PULSE / (60 * 4.5))

WiFiClient espClient;
PubSubClient mqtt_client(espClient);
WiFiManager wifiManager;

/* 
 * Global variables
 */
volatile int pulseflow=0;

/*
 * Counter pulse sensor
 */
void SensorInterrupt()
{
    pulseflow++;
}

/*
 * Indicator mode operation
 */
void mode_error()
{
   digitalWrite(GPIO_RED, 255);
   digitalWrite(GPIO_GREEN, 0);
   digitalWrite(GPIO_BLUE, 0);
}

void mode_config()
{
    digitalWrite(GPIO_RED, 0);
    digitalWrite(GPIO_GREEN, 0);
    digitalWrite(GPIO_BLUE, 255);
}

void mode_normal()
{
    digitalWrite(GPIO_RED, 0);
    digitalWrite(GPIO_GREEN, 0);
    digitalWrite(GPIO_BLUE, 0);
}

void mode_send()
{
    digitalWrite(GPIO_RED, 0);
    digitalWrite(GPIO_GREEN, 255);
    digitalWrite(GPIO_BLUE, 0);
} 

void reconnect() 
{
    while (!mqtt_client.connected()) {
#ifdef DEBUG
        Serial.print("Attempting MQTT connection...");
#endif
        if (mqtt_client.connect("ESP8266 Client")) {
#ifdef DEBUG
            Serial.println("MQTT Server Connected");
#endif
            mode_normal();
        } else {
            mode_error();

#ifdef DEBUG
            Serial.print("failed, rc=");
            Serial.print(mqtt_client.state());
            Serial.println(" try again in 5 seconds");
#endif      
      
            delay(5000);
        }
    }
}

void setup()
{
    Serial.begin(9600);

    pinMode(GPIO_RED, OUTPUT);
    pinMode(GPIO_GREEN, OUTPUT);
    pinMode(GPIO_BLUE, OUTPUT);
    pinMode(GPIO_RESET, INPUT);

    wifiManager.autoConnect();
    
    mqtt_client.setServer(MQTT_SERVER, MQTT_PORT);
    attachInterrupt(GPIO_SENSOR, SensorInterrupt, RISING);
}
 
void loop()
{
    char msg[256];
    int mycounter=0;
    float volume=0;
    int elapsedtime=0;

    /*
     * Check if is necessary new ESSID
     */
    if ( digitalRead(GPIO_RESET) ) {
        mode_error();
        
        while ( elapsedtime < ELAPSEDTIME && digitalRead(GPIO_RESET) ) {
            elapsedtime++;
            delay(1);
        }

        if ( elapsedtime >= ELAPSEDTIME && digitalRead(GPIO_RESET) ) {
          wifiManager.resetSettings();
          mode_error();
          delay(DEBOUNCE);
        } else {
          mode_normal();
        }
    }

    /*
     * Flow Sensor
     */
    while ( pulseflow > 0 ) {
        mycounter = mycounter + pulseflow;
        pulseflow = 0;

        mode_send();
        volume = LITERS(mycounter);

#ifdef DEBUG
        Serial.printf("\nPulses count: %d or %.2f liters.", mycounter, volume);
#endif

        delay(UPD_SENSOR);
    }

    /*
     * Server MQTT
     */
    if  ( volume > 0 ) {
        if (!mqtt_client.connected()) {
            reconnect();
        }
 
        sprintf(msg, "%f", volume);
  
        mqtt_client.publish(MQTT_TOPIC, msg);
        mode_normal();
    }
   
}

