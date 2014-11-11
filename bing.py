#!/usr/local/bin/python
from selenium import webdriver

import argparse
import os
import random
from time import sleep
import sys
import re
import time
import traceback

kMaxSleep = 5
kFBLoginLink = "https://www.facebook.com/login.php?skip_api_login=1&next=https%3A%2F%2Fwww.facebook.com%2Fdialog%2Foauth%3Fclient_id%3D111239619098%26auth_type%3Dhttps%26redirect_uri%3Dhttps%253A%252F%252Fssl.bing.com%252Ffd%252Fauth%252Fsignin%253Faction%253Dfacebook_oauth%2526provider%253Dfacebook%26from_login%3D1&cancel_uri=https%3A%2F%2Fssl.bing.com%2Ffd%2Fauth%2Fsignin%3Faction%3Dfacebook_oauth%26provider%3Dfacebook&api_key=111239619098"
kMSLoginLink = "https://login.live.com/login.srf?wa=wsignin1.0&rpsnv=11&ct=1367638624&rver=6.0.5286.0&wp=MBI&wreply=http:%2F%2Fwww.bing.com%2FPassport.aspx%3Frequrl%3Dhttp%253a%252f%252fwww.bing.com%252f&lc=1033&id=264960"
kAmazonRewardLink = 'http://www.bing.com/rewards/redeem/000100000004?meru=%252f'
kMinKeyDelay = 0.03
kMaxKeyDelay = 0.08
kMaxSearchErrors = 80

kErrorFile = "error.log"

# Dict of searchable phrases
phrases = {
   1:'How to make',        # <adjective> + <noun> + <adverb>
   2:'How to create',      # <adjective> + <noun> + <adverb>
   3:'Construct a',        # <adjective> + <noun> + <adverb>
   4:'Where can I find a', # <noun> + <adverb> + <adverb>
   4:'How to',             # <adverb> + <verb>
   5:'I want to'}          # <adverb> + <verb>

###
# Global Executions
###

# The following are global variables set here.
# args
# dirpath , the directory containing this executable
# dictdir , the directory containing the dictionary file
# adj, adv, nouns, verbs and corresponding byte files
# driver, the webdriver
# error , the exit status

# Parse command line args
parser = argparse.ArgumentParser()
parser.add_argument("login", help="login method", choices=['fb', 'ms'])
parser.add_argument("-d", "--virtual", help="run in virtual display",
                    action="store_true", default=False)
parser.add_argument("-n", "--numsearch", help="number of searches",
                    type=int, default=30)
parser.add_argument("-u", "--username", help="login username")
parser.add_argument("-p", "--password", help="login password")
parser.add_argument("-r", "--getrewards", help="attempt to redeem rewards",
                    action="store_true", default=False)
parser.add_argument("--dict",
                    help="absolute dictionary location if not in same directory",
                    default="")
parser.add_argument("--norandomsleep", help="don't simulate real user",
                    action="store_true", default=False)
parser.add_argument("--directory", help="the calling directory, if not from "
                                        "the script location", default=".")
args = parser.parse_args()
args.directory = args.directory + "/"

# Get directory path for dictionary file
# The dirpath is the location of the executable.
dirpath = re.match("^(.*)/([^/])*$", sys.argv[0]).group(1)

# The dictionary is at the same path as the executable
if args.dict == "":
  dictdir = dirpath + "/dict/"
else:
  dictdir = args.dict + "/"

# Open dictionary files
adj = open(dictdir + "adj.txt", 'r')
adv = open(dictdir + "adv.txt", 'r')
nouns = open(dictdir + "noun.txt", 'r')
verbs = open(dictdir + 'verb.txt', 'r')
adjectives_bytes = os.stat(dictdir + "adj.txt").st_size
adverbs_bytes = os.stat(dictdir + "adv.txt").st_size
nouns_bytes = os.stat(dictdir + "noun.txt").st_size
verbs_bytes = os.stat(dictdir + "verb.txt").st_size

# Record errors
error = 0

# check for virutal display
if args.virtual:
  if not 'linux' in sys.platform:
    print 'not running on linux, xvfb not present\ndefaulting to display'
    args.virtual = False
  else:
    print "attempting to run in virtual display"
    try:
      from pyvirtualdisplay import Display
      display = Display(visible=False, size=(800,600))
      display.start()
    except ImportError:
      print 'failed to find library pyvirtualdisplay'
      args.virtual = False

# Start webdriver
try:
  driver = webdriver.Chrome()
except:
  traceback.print_exc()
  print "failed to initialize webdriver"
  exit(1)

###
# End global executions
###

def write_error(msg):
  print msg
  global error
  error = 1
  errorfile = open(args.directory + kErrorFile, "a")
  errorfile.write(time.strftime("%d/%m/%Y") + "\n")
  errorfile.write("email: " + args.username + " account: " + args.login + "\n")
  errorfile.write(msg + "\n\n")
  errorfile.close()

def rand_sleep():
  if not args.norandomsleep:
    time.sleep(kMaxSleep * random.random())

def generate_search():
  num = random.randint(1, 5)
  if num == 1 or num == 2 or num == 3:
    phrase = phrases[num] + " " + random_line(adj, adjectives_bytes) + " " + random_line(nouns, nouns_bytes) + " " + random_line(adv, adverbs_bytes)
  else:
    phrase = phrases[num] + " " + random_line(adv, adverbs_bytes) + " " + random_line(verbs, verbs_bytes)
  return phrase    

def emulate_typing(text_field, string):
  for i in range(len(string)):
    text_field.send_keys(string[i])
    sleep(random.uniform(kMinKeyDelay, kMaxKeyDelay))
  sleep(random.uniform(kMinKeyDelay, kMaxKeyDelay))


def random_line(dictionary, total_bytes):
  dictionary.seek(random.randint(0, total_bytes - 15))
  dictionary.readline()
  return dictionary.readline().strip('\n')

def get_bonus_rewards(xpath_id):
  print "Attempting to get bonus rewards at xpath: " + xpath_id
  rand_sleep()
  driver.get('http://www.bing.com/rewards/dashboard')

  # print the currently available points
  try:
    points_available_xpath = driver.find_element_by_xpath('//*[@id="user-status"]/span[2]/div[1]')
    points_available = points_available_xpath.text
    print "before attempting bonus points, current points: " + points_available
  except:
    print "failed to check points available"

  full_xpath = "//*[contains(@href,'" + xpath_id + "')]"
  mylist = driver.find_elements_by_xpath(full_xpath)
  numlinks = len(mylist)
  if numlinks == 0:
    print "no bonus points possible"
    return

  first = 0
  if 'Connect to Facebook' in mylist[first].text:
    first = 1

  bonus_points_clicked = 0
  for i in range(numlinks):
    try:
      rand_sleep()
      mylist[first].click()
      bonus_points_clicked += 1
    except:
      print "couldn't click element"

    rand_sleep()
    driver.get('http://www.bing.com/rewards/dashboard')
    mylist = driver.find_elements_by_xpath(full_xpath)

  print "clicked " + str(bonus_points_clicked) + " bonus links"

def do_search():
  search_count = 0
  error_count = 0
  while search_count < args.numsearch and error_count < kMaxSearchErrors:
    try:
      search_bar = driver.find_element_by_xpath('//*[@id="sb_form_q"]')
      search_button = driver.find_element_by_xpath('//*[@id="sb_form_go"]')
    except:
      print "failed to select searchbar or searchbutton"
      error_count += 1
      continue

    rand_sleep()
    search_string = generate_search()
    search_bar.clear()

    emulate_typing(search_bar, search_string)
    try:
      search_button.click()
      search_count += 1
    except:
      print "failed to click search_botton"
      error_count += 1

  print "executed " + str(search_count) + " searches"
  if search_count < args.numsearch:
    write_error("expected " + str(args.numsearch) + " searches but had " +
                str(search_count))

def main():
  # seed random number generator with current system time
  random.seed(time.time())

  # start driver and login
  login = True
  try:
    # Sign into facebook or microsoft
    if args.login == "fb":
      driver.get(kFBLoginLink)
      email_form = driver.find_element_by_xpath('//*[@id="email"]')
      emulate_typing(email_form, args.username)
      pass_form = driver.find_element_by_xpath('//*[@id="pass"]')
      pass_form.clear()
      emulate_typing(pass_form, args.password)
      driver.find_element_by_xpath('//*[@id="u_0_1"]').click()

    elif args.login == "ms":
      driver.get(kMSLoginLink)
      email_form = driver.find_element_by_xpath('//*[@id="i0116"]')
      emulate_typing(email_form, args.username)
      pass_form = driver.find_element_by_xpath('//*[@id="i0118"]')
      pass_form.clear()
      emulate_typing(pass_form, args.password)
      driver.find_element_by_xpath('//*[@id="idSIButton9"]').click()

    search_bar = driver.find_element_by_xpath('//*[@id="sb_form_q"]')
    emulate_typing(search_bar, "start")
    driver.find_element_by_xpath('//*[@id="sb_form_go"]').click()
    print 'login successful to account ' + args.username + " at " + args.login
  except:
    write_error("login failed")
    login = False

  if login:
    # run searches
    do_search()

    # get bonus rewards (i.e. via link clicking)
    print 'getting bonus points'
    try:
      get_bonus_rewards("rewardsapp")
    except:
      "ERROR: failed to get bonus rewards due to exception"
    #get_bonus_rewards("rewards/challenge")

    # attempt to redeem rewards
    should_redeem = True
    if args.getrewards:
      print 'attempting to get rewards'
      rand_sleep()
      try:
        driver.get(kAmazonRewardLink)
      except:
        write_error("failed to get amazon rewards link")
        should_redeem = False

    if should_redeem:
      print 'attempting to redeem reward'
      try:
        reward_button = driver.find_element_by_xpath(
              "//*[@id='SingleProduct_SubmitForm']")
      except:
        print 'insufficient reward points at this time or bad link'
        should_redeem = False

    if should_redeem:
      try:
        rand_sleep()
        reward_button.click()
        confirm_button = driver.find_element_by_xpath(
            "//*[@id='CheckoutReview_SubmitForm']")
        rand_sleep()
        confirm_button.click()
        rand_sleep()
      except:
        write_error("failed to redeem rewards")

  exit(error)

try:
  main()
finally:
  driver.quit()

  # stop virtual display
  if args.virtual:
    display.stop()
