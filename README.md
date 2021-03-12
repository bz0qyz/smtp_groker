---
title: AWSDEPLOY
section: 1
header: User Manual
date: March 12, 2021
lang: en-US
---
# NAME
smtp_groker - CLI script used to test SMTP server with SSL, TLS and Authentication.

# Prerequisites
- Python Modules
  - import argparse
  - logging
  - smtplib
  - json
  - getpass
  - pathlib

# CONFIGURATION
Configuration profiles can be saved so all parameters don't need to be used for every test. The profiles are saved in json format in the user home directory.

# SYNOPSIS
**smtp_groker.py** [*options*]

# DESCRIPTION
**smtp_groker.py** is a python script for testing SMTP servers.

# OPTIONS
- \-h | \-\-help            
  - Show help message and exit
- \-T | \-\-tls
  - Use TLS Authntication
- \-S | \-\-ssl
  - Use an SSL Connection. Implies no TLS.
- \-p SMTP_PORT | \-\-port SMTP_PORT
  - SMTP Server port. defaults to 587 or 465 for SSL
- \-d | \-\-dry-run         
  - Test connection and authentication, but do not send an email message.
- \-v, \-\-verbose
  - Show verbose output.
- \-\-profile PROFILE
  - Use a saved configuration profile by this name.
- \-H SMTP_HOST | \-\-host SMTP_HOST
  - SMTP Server hostname or IP address
- \-u SMTP_USER, \-\-user SMTP_USER
  - SMTP User. Using this argument enables SMTP Authentication.
- \-P SMTP_PASSWORD, \-\-password SMTP_PASSWORD
  - SMTP password.
- \-s SENDER, \-\-sender SENDER
  - email address of the sender.
- \-r RECIPIENT|  \-\-recipient RECIPIENT
  - email address of the recipient. Can be used multiple times.
- \-\-save SAVE_PROFILE
  - Store the passed configuration as a test profile with this name.

# EXAMPLES
**smtp_groker.py -H 10.0.0.58 -s sender@domain1.com -r recipient1@domain1.com -r recipient2@domain1.com -u larry -P 'p@ssw0rd' --tls**

**smtp_groker.py -H 10.0.0.58 -s sender@domain2.com -r recipient1@domain2.com  -u bob -P 'p@ssw0rd' --ssl --dry-run -v**

# AUTHORS
Written By: Russ Cook <bz0qyz@gmail>. Russ is not a real developer so cut him some slack when reviewing his code.
