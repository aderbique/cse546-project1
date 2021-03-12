#!/bin/bash

cd /home/ec2-user/cse546-project1/server && \
	git pull origin master && \
        python3 app.py
