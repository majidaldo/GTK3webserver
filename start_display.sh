#!/bin/bash

#supply a 1. display number and 2. a port num as args
#. could be the same

exec broadwayd -p $2 :$1  #&

exit 0
