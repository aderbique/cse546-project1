# cse546-project1
Cloud Computing Project One for ASU CSE546 Spring 21

## Contributors
- Austin Derbique
- Alexander Pappas
- Cole Ruter

## Overview


## Instructions for Deployment

### Webserver
To start the webserver, log into the EC2 instance as user `ec2-user`. Then, simply execute the following commands
```
$ tmux
$ cd ~/cse546-project1/server
$ python app.py
```

If in the event that the webserver is already running and needs to be stopped, you can attach yourself to the tmux process to kill the application
```
$ tmux -a
```

## Instructions for Using image recognition service
