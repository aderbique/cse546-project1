#!/bin/bash
export RUN_CONTINUOUSLY=True && \
cd /home/ubuntu/cse546-project1/classifier && \
	git pull && \
	python3 main.py
