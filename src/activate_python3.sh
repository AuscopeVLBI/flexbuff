#!/bin/bash
echo 'Activating Python 3.8.5 environment'
# source bashrc for crontab to transition from shell 2 bash
source ~/.bashrc

# overwrite pythonpath set by DiFX and set python3 env
export PYTHONPATH=/home/observer/.pyenv/shims/python
pyenv shell 3.8.5
