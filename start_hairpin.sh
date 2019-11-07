#!/bin/bash

source venv/bin/activate
nohup python hairpin.py > var/log/hairpin.log 2>&1 &
