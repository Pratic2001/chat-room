#!bin/bash

function ctrl_c(){
	killall python3;
	killall ngrok;
	exit 0;
}

. ~/anaconda3/bin/activate chat_room;
killall python3; 
python3 server.py &
killall ngrok; 
ngrok http --domain=firstly-magnetic-sparrow.ngrok-free.app http://localhost:5000 &

while :
do
	trap ctrl_c SIGINT;
done
exit 0;
