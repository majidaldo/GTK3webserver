#!/bin/bash

#supply a port and a display number. could be the same

exec broadwayd -p $2 :$1  #&

exit 0
