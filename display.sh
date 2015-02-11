#!/bin/bash

#supply a 'display' number which is the same as the port number

kill_child_processes() {
    isTopmost=$1
    curPid=$2
    childPids=`ps -o pid --no-headers --ppid ${curPid}`
    for childPid in $childPids
    do
        kill_child_processes 0 $childPid
    done
    if [ $isTopmost -eq 0 ]; then
        kill -9 $curPid 2> /dev/null
    fi
}
 
# Ctrl-C trap. Catches INT signal
trap "kill_child_processes 1 $$; exit 0" INT

broadwayd -p $1 :$1  &
GDK_BACKEND=broadway BROADWAY_DISPLAY=:$1 UBUNTU_MENUPROXY= LIBOVERLAY_SCROLLBAR=0 python app.py 

kill_child_processes 1 $$
exit 0
