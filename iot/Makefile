all: compile
	
compile: 
	gcc src/daemon.c src/database.h src/block.h -lpaho-mqtt3c -lsqlite3 -o daemon
clear:
	rm -rf *.o* *.~ daemon

