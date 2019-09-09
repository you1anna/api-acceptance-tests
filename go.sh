#!/usr/bin/env bash

export PATH=$PATH:$(pwd)
#brew install autoconf automake libtool
pip3 install --upgrade pip
python3 -m venv venv
source ./venv/bin/activate
pip3 install .
#python3 -m pip3 install -r requirements.txt --disable-pip-version-check