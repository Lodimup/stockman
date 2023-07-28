#! /bin/bash

PRE='export $(cat '
POST='/.env | xargs)'
CMD=$PRE$1$POST
echo $CMD >> ~/.bashrc

apt update && sudo apt upgrade -y && sudo apt install cmake -y
poetry config virtualenvs.in-project true
poetry install
