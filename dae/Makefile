all: compile
debug: compile_debug

compile: 
	gcc -c database.c -o database.o 
	gcc subscriber.c database.o -lpq -lpaho-mqtt3c -o ../subscriber

compile_debug: 
	gcc -c database.c -DDEBUG -o database.o 
	gcc subscriber.c database.o -lpq -lpaho-mqtt3c -DDEBUG -o ../subscriber

clear:
	rm  *.o* *.~ ../subscriber

