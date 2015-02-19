#!/bin/bash

#
mydir=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
cd $mydir
python serve.py

