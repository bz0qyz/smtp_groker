#!/usr/bin/env python

import argparse
import sys, os
import logging
import smtplib
import json
from getpass import getpass
from pathlib import Path

"""
## Global Variables
"""
## Name of this application
PROG = "smtp_groker"
## Version of this application
VERSION = "1.0.0"
## Description of this application
DESCRIPTION = "Script used to test SMTP server with SSL, TLS and Authentication. This is overkill, I get it."
## Git URL for the project
GIT_URL = "https://github.com/bz0qyz/smtp_groker"
## Location of the saved profiles file
PROFILE_FILE = "{}{}.{}.json".format(Path.home(), os.sep,PROG)


"""
## Process command-line arguments
"""
parent_parser = argparse.ArgumentParser(prog="{} ver.{}".format(PROG, VERSION), description=DESCRIPTION, add_help=False)
parent_parser.add_argument("-T", "--tls", dest="use_tls", action="store_true", default=False, help="Use TLS Authntication")
parent_parser.add_argument("-S", "--ssl", dest="use_ssl", action="store_true", default=False, help="Use an SSL Connection. Implies no TLS.")
parent_parser.add_argument("-p", "--port", dest='smtp_port', default=587, type=int, help="SMTP Server port. defaults to 587 or 465 for SSL")
parent_parser.add_argument('-d', '--dry-run', action="store_true", default=False, help="Test connection and authentication, but do not send an email message.")
parent_parser.add_argument('-v', '--verbose', action="count", default=0, help="Show verbose output.")
parent_parser.add_argument("--profile", dest='profile', help="Use a saved configuration profile by this name.")
parser = argparse.ArgumentParser(parents=[parent_parser])
if not '--profile' in sys.argv:
    parser.add_argument("-H", "--host", dest='smtp_host', default="localhost", help="SMTP Server hostname or IP address", required=True)
    parser.add_argument("-u", "--user", dest='smtp_user', help="SMTP User. Using this argument enables SMTP Authentication.")
    parser.add_argument("-P", "--password", dest='smtp_password', help="SMTP password.")
    parser.add_argument("-s", "--sender", help="email address of the sender.", required=True)
    parser.add_argument("-r", "--recipient", action='append', help="email address of the recipient. Can be used multiple times.", required=True)
    parser.add_argument("--save", dest='save_profile', help="Store the passed configuration as a test profile with this name.")
args = parser.parse_args()

"""
## Configure Console Logging
"""
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

logging.addLevelName(logging.INFO, '{}[INFO]{}'.format(bcolors.OKGREEN, bcolors.ENDC))
logging.addLevelName(logging.WARNING, '{}[WARNING]{}'.format(bcolors.WARNING, bcolors.ENDC))
logging.addLevelName(logging.ERROR, '{}[ERROR]{}'.format(bcolors.FAIL, bcolors.ENDC))
logging.addLevelName(logging.CRITICAL, '{}[CRITICAL]{}'.format(bcolors.FAIL, bcolors.ENDC))
logging.addLevelName(logging.DEBUG, '{}[DEBUG]{}'.format(bcolors.OKCYAN, bcolors.ENDC))
logging.addLevelName(60, '{}[RESULT]{}'.format(bcolors.OKBLUE, bcolors.ENDC),)
LOG_FORMAT = '%(levelname)s %(message)s' if args.verbose < 2 else '{}(%(module)s:%(lineno)d){} - %(levelname)s %(message)s'.format(bcolors.HEADER, bcolors.ENDC)
logging.basicConfig(format=LOG_FORMAT)
log = logging.getLogger()

if args.verbose > 0:
    log.setLevel(logging.DEBUG)
elif args.verbose == 1:
    log.setLevel(logging.WARNING)
else:
    log.setLevel(logging.INFO)

"""
## Class Objects
"""
class Profiles():
    """Object for working with the saved profiles."""
    def __init__(self, profiles_file):
        self.file = profiles_file
        self.profiles = self.__load_profiles(file=self.file)

    def __load_profiles(self, file):
        """ Open the profiles file and read the contents """

        if os.path.isfile(file):
            log.debug("Loading profiles file: {} ".format(file))
            try:
                with open(file) as json_file:
                    return json.load(json_file)
            except ValueError as Err:
                log.critical("Error decoding json profiles file: " + config_file + "\nDetails: " + str(Err))
                sys.exit(2)
        else:
            return {}

    def __save_profiles(self, file):
        """ Save the profiles to the file """
        log.debug("Saving profiles to file: {}".format(file))
        with open(file, 'w') as outfile:
            json.dump(self.profiles, outfile, indent=True, sort_keys=True)

    def save(self, name, profile):
        """ Save a profile to the profiles file """
        if name in self.profiles:
            log.warning("Profile already exists. overwriting it.")
        self.profiles[name] = profile
        self.__save_profiles(file=self.file)
        return True

    def get(self, name):
        """ Fetch a profile by name """
        log.debug("Get saved profile name: {}".format(name))
        if name in self.profiles:
            return self.profiles[name]
        else:
            raise ValueError("Saved profile: {}. Does not exist".format(name))


"""
## Functions
"""
def closeup():
    try:
        smtpObj.quit()
        log.debug("Closing connection to SMTP host")
    except:
        pass
    quit()

def print_resp(bytestring):
    tlist = []
    for item in bytestring:
        try:
            tlist.append(item.decode('utf-8'))
        except:
            tlist.append(str(item))
    log.log(60, " - ".join(tlist))

def print_smtp_except(err):
    if hasattr(err, "smtp_error"):
        log.critical(err.smtp_error.decode('utf-8'))
    elif hasattr(err, "recipients"):
        log.error("One or more recipients failed.")
        for key, val in err.recipients.items():
           log.error("{}: {}".format(key, val))
    elif hasattr(err, "sender"):
        log.error("Failed to meet sender restrictions.")
        log.error(err.sender)
    else:
        if err:
          if isinstance(err, dict):
              for key, val in err.items():
                  log.error("{}: {}".format(key, val))
          else:
              log.critical(err)

"""
## Main Section
"""

""" Load or Create a profile for execution """
objProfiles = Profiles(PROFILE_FILE)
if "profile" in args and args.profile:
    """ Open a saved profile if '--profile' is specified """
    profile = objProfiles.get(args.profile)
else:
    profile = {
        "host": args.smtp_host,
        "user": args.smtp_user,
        "password": args.smtp_password,
        "sender": args.sender,
        "recipient": args.recipient
    }
    profile["auth"] = True if args.smtp_user else False


""" Save arguments to a profile if '--save' is specified """
if "save_profile" in args and args.save_profile:
    log.info("Saving profile: {}".format(args.save_profile))
    objProfiles.save(args.save_profile, profile)

""" If SSL is used, change the port to smtps (465) """
if args.use_ssl and args.smtp_port == 587:
    args.smtp_port = 465

""" If a user is specified and no password, prompt for the password """
if profile["auth"] and not profile["password"]:
    profile["password"] = getpass(prompt="Enter a password for SMTP user '{}': ".format(args.smtp_user))

""" Open a connection to the SMTP Host """
try:
    log.debug("Opening SMTP connection to: {}:{}".format(profile["host"], args.smtp_port))
    if args.use_ssl:
        args.use_tls = False # disable TLS if we are using SSL
        log.debug("SSL Connection in use")
        smtpObj = smtplib.SMTP_SSL(profile["host"], args.smtp_port, timeout=5)
    else:
        smtpObj = smtplib.SMTP(profile["host"], args.smtp_port, timeout=5)
except Exception as e:
    log.error("Unable to connect to mail host: {}:{}".format(profile["host"], args.smtp_port))
    print_smtp_except(e)
    closeup()


""" Perform authentication on SMTP host """
if "auth" in profile and profile["auth"]:
    try:
        if args.use_tls:
            log.debug("TLS Authentication in use")
            retval = smtpObj.starttls()
            print_resp(retval)
            smtpObj.ehlo()

        log.debug("Authenticating as user: {}".format(profile["user"]))
        retval = smtpObj.login(profile["user"], str(profile["password"]))
        print_resp(retval)
    except Exception as e:
        print_smtp_except(e)
        closeup()

""" Craft the email message """
message = """From: {s}
To: {r}
Subject: SMTP e-mail test

This is a test e-mail message.
powered by {a} - {u}

-------------------------------------
Parameters:
-------------------------------------
 - Host: {h}:{p}
 - TLS: {t}
 - SSL: {l}
""".format(
        s=profile["sender"],
        r="\r\nTo: ".join(profile["recipient"]),
        t=args.use_tls,
        l=args.use_ssl,
        h=profile["host"],
        p=args.smtp_port,
        a=PROG,
        u=GIT_URL
    )
log.debug("Sending Message:\n{}".format(message))


""" Send the email mssage """
if not args.dry_run:
    try:
        retval = smtpObj.sendmail(profile["sender"], profile["recipient"], message)
        log.info("Successfully sent email for one or more recipients .")
        print_smtp_except(retval)
        closeup()
    except Exception as e:
        print_smtp_except(e)
        closeup()
else:
    log.info("Dry-run enabled. No message sent")
    closeup()
