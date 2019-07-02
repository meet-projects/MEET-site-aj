#!/bin/bash

which python3
exists=$?
if [ exists = 1 ]
then
	echo "Python3 not installed, you have failed"
else 
	which virtualenv
	exists=$?
	if [ exists = 1 ]
	then
		echo "virtualenv does not exist - installing now"
		pip3 install virtualenv
	fi
	virtualenv meet-web
	source meet-web/bin/activate

	pip3 install -r requirements.txt
	python3 app.py 
	deactivate
	rm -r meet-web
fi