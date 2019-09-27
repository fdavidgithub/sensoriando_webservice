#/bin/bash

KEY=/home/fdavid/.ssh/AccessEC2.pem 
USER=ubuntu
HOST=$USER@sensoriando

scp -r -i $KEY $1 $HOST:/home/$USER    


