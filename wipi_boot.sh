#!/bin/bash
# wipi_boot daemon
# chkconfig: 345 20 80
# description: wipi_boot daemon
# processname: wipi_boot



#	http://werxltd.com/wp/2012/01/05/simple-init-d-script-template/

# cp wipi_boot.sh /etc/init.d/

# update-rc.d wipi_boot defaults

DAEMON=gunicorn
DAEMONOPTS="-b 0.0.0.0:8888 autoapp:app"

DAEMON_PATH="/home/pi/wipiServer"

NAME=wipi_boot
DESC="WiPi boot script"
PIDFILE=/var/run/$NAME.pid
SCRIPTNAME=/etc/init.d/$NAME

case "$1" in
start)
	printf "%-50s" "Starting $NAME..."
	cd $DAEMON_PATH
    source ./bin/activate
    source .env	
	PID=`$DAEMON $DAEMONOPTS > /dev/null 2>&1 & echo $!`
	echo "Saving PID" $PID " to " $PIDFILE
        if [ -z $PID ]; then
            printf "%s\n" "Fail"
        else
            echo $PID > $PIDFILE
            printf "%s\n" "Ok"
        fi
;;
stop)
        printf "%-50s" "Stopping $NAME"
            PID=`cat $PIDFILE`
            cd $DAEMON_PATH
        if [ -f $PIDFILE ]; then
            kill -HUP $PID
            printf "%s\n" "Ok"
            rm -f $PIDFILE
        else
            printf "%s\n" "pidfile not found"
        fi
;;
restart)
  	$0 stop
  	$0 start
;;

*)
        echo "Usage: $0 {status|start|stop|restart}"
        exit 1
esac
