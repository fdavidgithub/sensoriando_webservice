#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <MQTTClient.h>

#include "database.h"
#include "block.h"

#define DEBUG

#define MQTT_SERVER "200.159.88.174"
#define MQTT_TOPIC  "geral/esp"
#define MQTT_ID     "Broker"
#define MQTT_QOS    0
/*
 *  Global variables
 */
struct Block block_stream;
struct Data data_watter;
struct Db database;

void delivered(void *context, MQTTClient_deliveryToken dt)
{
/*
    MQTTClient client;
    MQTTClient_connectOptions conn_opts = MQTTClient_connectOptions_initializer;
    MQTTClient_message pubmsg = MQTTClient_message_initializer;
    MQTTClient_deliveryToken token;
    int rc;
    char payload[256];
    
#ifdef DEBUG
    printf("Processing delivery\n");
#endif

    if ( db_init(&database, "mqtt.db") ) {
        perror("db_init: ");
        exit(1);
    }
        
    if ( db_select(&database, &data_watter) == 0 ) { 
        perror("on select: ");
    }

    db_end(&database);

#ifdef DEBUG
    printf("\tTotal liters: %f\n", data_watter.liters); 
#endif

    sprintf(payload, "%.2f", data_watter.liters);

    MQTTClient_create(&client, MQTT_SERVER, MQTT_ID, MQTTCLIENT_PERSISTENCE_NONE, NULL);
    conn_opts.keepAliveInterval = 20;
    conn_opts.cleansession = 1;

    if ((rc = MQTTClient_connect(client, &conn_opts)) != MQTTCLIENT_SUCCESS)
    {
        printf("Fail while connect publisher, return code %d\n", rc);
        exit(EXIT_FAILURE);
    }

    pubmsg.payload = payload;
    pubmsg.payloadlen = (int)strlen(payload);
    pubmsg.qos = MQTT_QOS;
    pubmsg.retained = 0;
    
    MQTTClient_publishMessage(client, "geral/esp2", &pubmsg, &token);

#ifdef DEBUG
    printf("Waiting for up to %d seconds for publication of %s\n"
            "on topic %s for client with ClientID: %s\n",
            (int)(10000/1000), payload, "geral/esp2", MQTT_ID);
#endif

    rc = MQTTClient_waitForCompletion(client, token, 10000);

#ifdef DEBUG    
    printf("Message with delivery token %d delivered\n", token);
#endif

    MQTTClient_disconnect(client, 10000);
    MQTTClient_destroy(&client);
*/
}

int on_message(void *context, char *topicName, int topicLen, MQTTClient_message *message) 
{
    char* payload = message->payload;

#ifdef DEBUG
    printf("Topic: %s Message: %f\n", topicName, atof(payload));
#endif

    block_stream.liters = atof(payload);

    if ( db_init(&database, "mqtt.db") ) {
        perror("db_init: ");
        exit(1);
    }

    if ( db_insert(&database, &block_stream) ) {
        perror("db_insert: ");
    }

    db_end(&database);

    MQTTClient_freeMessage(&message);
    MQTTClient_free(topicName);

    return 1;
}

int main(int argc, char *argv[])
{
   MQTTClient client;
   MQTTClient_connectOptions conn_opts = MQTTClient_connectOptions_initializer;
    int rc;
    int ch;

   /* 
    * Init MQTT (conect & subscribe) 
    */
   MQTTClient_create(&client, MQTT_SERVER, MQTT_ID, MQTTCLIENT_PERSISTENCE_NONE, NULL);

    conn_opts.keepAliveInterval = 20;
    conn_opts.cleansession = 1;
   
   MQTTClient_setCallbacks(client, NULL, NULL, on_message, delivered);

   rc = MQTTClient_connect(client, &conn_opts);

   if (rc != MQTTCLIENT_SUCCESS)
   {
       printf("Fail while connect subscriber, return code: %d\n", rc);
       exit(-1);
   }

   MQTTClient_subscribe(client, MQTT_TOPIC, MQTT_QOS);
   
   while (1) {       

   }
}

