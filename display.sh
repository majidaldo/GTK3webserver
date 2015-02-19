#!/bin/sh

#to run an application on a display
#supply the command as the first arg
#the second arg is the broadway display number

DISPLAY=:$2 GDK_BACKEND=broadway BROADWAY_DISPLAY=:$2 UBUNTU_MENUPROXY= LIBOVERLAY_SCROLLBAR=0 exec $1

exit 0
