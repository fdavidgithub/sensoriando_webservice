#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <MQTTClient.h>

#include "database.h"

#define MQTT_TOPIC  "#"
#define MQTT_ID     "Broker"
#define MQTT_QOS    2 /* Once and one only - the message will be delivered exactly once. */

#define LEN_BUFFER 256

/*
 * Constants
 */
const char help_param[]     = "-h";
const char config_param[]   = "-c";
const char verbose_param[]  = "-v";

/*
 *  Global variables
 */
int verbose = 0;
char config_file[LEN_BUFFER]   = "sensoriando.conf";

char db_host[LEN_BUFFER];
char db_name[LEN_BUFFER];
char db_username[LEN_BUFFER];
char db_password[LEN_BUFFER];

char mqtt_server[LEN_BUFFER];
char mqtt_username[LEN_BUFFER];
char mqtt_password[LEN_BUFFER];

/*
 * Prototypes
 */
int on_message(void *, char *, int, MQTTClient_message *);
void msg_storage(char *, char *);
void print_help();
void setconfig();

/*
 * Main
 */
int 
main(int argc, char *argv[])
{
    MQTTClient client;
    MQTTClient_connectOptions conn_opts = MQTTClient_connectOptions_initializer;
    int rc;
    int ch;
    int i;

    /*
     * Check params
     */
    for ( i=1; i<argc; i++) {
        if ( strncmp(argv[i], help_param, sizeof(help_param)) == 0 ) {
            print_help();
            return 1;
        }

        if ( strncmp(argv[i], verbose_param, sizeof(verbose_param)) == 0 ) {
            verbose = 1;
        }

        if ( strncmp(argv[i], config_param, sizeof(config_param)) == 0 ) {
            i++;
            strcpy(config_file, argv[i]);
        }
    }

    setconfig(); 
    
    /*
     * Show params
     */
    if ( verbose ) {
        printf("Config file: %s\n", config_file);
        printf("\nMQTT Settings\n");
        printf("Broker: %s\n", mqtt_server);
        printf("Username: %s\n", mqtt_username);
        printf("Password: %s\n", mqtt_password);
        printf("\nPostgreSQL Settings\n");
        printf("Host: %s\n", db_host);
        printf("Name: %s\n", db_name);
        printf("Username: %s\n", db_username);
        printf("Password: %s\n", db_password);
        
        printf("\n");
    }

    /* 
     * Init MQTT (conect & subscribe) 
     */
    rc = MQTTClient_create(&client, mqtt_server, MQTT_ID, MQTTCLIENT_PERSISTENCE_NONE, NULL);

    if ( rc != MQTTCLIENT_SUCCESS ) {
	    printf("Error on create MQTTClient, return code: %d\n", rc);
	    return 1;
    }

    conn_opts.keepAliveInterval = 20;
    conn_opts.cleansession = 1;
    conn_opts.username = mqtt_username;
    conn_opts.password = mqtt_password; 

    MQTTClient_setCallbacks(client, NULL, NULL, on_message, NULL);

    rc = MQTTClient_connect(client, &conn_opts);

    if (rc != MQTTCLIENT_SUCCESS) {
       printf("Fail while connect subscriber, return code: %d\n", rc);
       return rc;
    }

    MQTTClient_subscribe(client, MQTT_TOPIC, MQTT_QOS);

    if ( verbose ) {
        printf("\nWaiting payload... \n");
    }

   
    while (1) {       

    }
}

/*
 * Functions
 */
int 
on_message(void *context, char *topicName, int topicLen, MQTTClient_message *message) 
{
    char* payload = message->payload;

    if ( verbose ) {
        printf("Topic: %s\n", topicName);
        printf("Message: %s\n", payload);
    }

    msg_storage(topicName, payload);

    MQTTClient_freeMessage(&message);
    MQTTClient_free(topicName);

    return 1;
}

void 
msg_storage(char *topic, char *payload)
{
    PGconn *conn = do_connect(db_name, db_username, db_password, db_host);
    Thing *thing;
    Datum datum;
    char dt_stream[14];
    float value;
    int id_sensor;

    if ( conn ) {
        if ( verbose ) {
            printf("\tPosgresSQL Connected!\n");
        }

        thing = thing_serialkey_get(conn, topic);

        if ( thing != NULL ) {
            strcpy(datum.payload, payload);
            datum.id_thing = thing->id; 

            if ( verbose ) {
                sscanf(payload, "{\"dt\":\"%14s\", \"sensor\":%d, \"value\":%f}", dt_stream, id_sensor, value);

                printf("\tThing ID#%d Name: %s\n", thing->id, thing->name);
                printf("\tTopic: %s\n\n", thing->token);
                printf("\tSensor ID#%d\n", id_sensor);
                printf("\tPayload: %s\n", payload);
                printf("\tDt Stream: %s\n", dt_stream);
                printf("\tValue: %f\n", value);
                printf("\n");
            }

            if ( !data_insert(conn, &datum) ) {
                printf("Error while insert datum of sensor\n");    
            }
        }

        do_exit(conn);
    }
}

void 
print_help()
{
    printf("Usage: subscriber\n");
    printf("%s\tThis help\n", help_param);
    printf("%s\tMode Verbose\n", verbose_param);
    printf("%s\tConfig file, default: %s\n", config_param, config_file);
}

void 
setconfig()
{
    FILE *fd;
    char buffer[LEN_BUFFER];

    /*
     * Config file
     */
    fd = fopen(config_file, "r");

//    if ( fd == NULL ) {
//        savelog(LOG_ERROR_CONFIG);
//    }

    while ( ! feof(fd) ) {
        fgets( buffer, LEN_BUFFER, fd );

        if ( buffer[0] != '#' ) {
            if ( strstr(buffer, "mqtt_host") ) {
                sscanf(buffer, "mqtt_host=%s\n", mqtt_server);
            }

            if ( strstr(buffer, "mqtt_user") ) {
                sscanf(buffer, "mqtt_user=%s\n", mqtt_username);
            }

            if ( strstr(buffer, "mqtt_passwd") ) {
                sscanf(buffer, "mqtt_passwd=%s\n", mqtt_password);
            }

            if ( strstr(buffer, "db_host") ) {
                sscanf(buffer, "db_host=%s\n", db_host);
            }
 
            if ( strstr(buffer, "db_name") ) {
                sscanf(buffer, "db_name=%s\n", db_name);
            }
 
            if ( strstr(buffer, "db_user") ) {
                sscanf(buffer, "db_user=%s\n", db_username);
            }

            if ( strstr(buffer, "db_passwd") ) {
                sscanf(buffer, "db_passwd=%s\n", db_password);
            }

        }
    }

    fclose(fd);
}
