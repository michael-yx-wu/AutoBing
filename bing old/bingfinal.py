#!/usr/bin/python
import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import argparse
import os
from random import randint
import sys
import re

# parse command line args
parser = argparse.ArgumentParser()
parser.add_argument("login", help="login method", choices=['fb', 'ms'])
parser.add_argument("-d", "--virtual", help="run in virtual display", action="store_true", default=False)
parser.add_argument("-n", "--numsearch", help="number of searches", type=int, default=30)
parser.add_argument("-u", "--username", help="login username")
parser.add_argument("-p", "--password", help="login password")
parser.add_argument("--dict", help="abs dictionary location if not in same dir", default="")
args = parser.parse_args()

dirpath = re.match("^(.*)/([^/])*$",sys.argv[0]).group(1)
if args.dict == "":
    dictdir = dirpath + "/dict/"
else:
    dictdir = args.dict + "/"

# open dictionary files
adj = open(dictdir + "adj.txt", 'r')
adv = open(dictdir + "adv.txt", 'r')
nouns = open(dictdir + "noun.txt", 'r')
verbs = open(dictdir + 'verb.txt', 'r')
adjectives_bytes = os.stat(dictdir + "adj.txt").st_size
adverbs_bytes = os.stat(dictdir + "adv.txt").st_size
nouns_bytes = os.stat(dictdir + "noun.txt").st_size
verbs_bytes = os.stat(dictdir + "verb.txt").st_size

# Dict of searchable phrases
phrases = {1:'How to make',        # <adjective> + <noun> + <adverb>
           2:'How to create',      # <adjective> + <noun> + <adverb>
           3:'Construct a',        # <adjective> + <noun> + <adverb>
           4:'Where can I find a', # <noun> + <adverb> + <adverb> 
           4:'How to',             # <adverb> + <verb>
           5:'I want to'}          # <adverb> + <verb>


def generate_search():
    num = randint(1, 5)
    if num == 1 or num == 2 or num == 3:
        phrase = phrases[num] + " " + random_line(adj, adjectives_bytes) + " " + random_line(nouns, nouns_bytes) + " " + random_line(adv, adverbs_bytes)
    else:
        phrase = phrases[num] + " " + random_line(adv, adverbs_bytes) + " " + random_line(verbs, verbs_bytes)
    return phrase    

def random_line(dictionary, total_bytes):
    dictionary.seek(randint(0, total_bytes-15))
    dictionary.readline()
    return dictionary.readline().strip('\n')

# check for virutal display
if args.virtual:
    if not 'linux' in sys.platform:
        print 'not running on linux, xvfb not present\ndefaulting to display'
        args.virtual = False
    else:
        try:
            from pyvirtualdisplay import Display
            display = Display(visible=False, size=(800,600))
            display.start()
        except ImportError:
            print 'failed to find library pyvirtualdisplay'
            args.virtual = False

# start driver and login
driver = webdriver.Chrome()
if args.login == "fb":
    driver.get("https://www.facebook.com/login.php?skip_api_login=1&next=https%3A%2F%2Fwww.facebook.com%2Fdialog%2Foauth%3Fclient_id%3D111239619098%26auth_type%3Dhttps%26redirect_uri%3Dhttps%253A%252F%252Fssl.bing.com%252Ffd%252Fauth%252Fsignin%253Faction%253Dfacebook_oauth%2526provider%253Dfacebook%26from_login%3D1&cancel_uri=https%3A%2F%2Fssl.bing.com%2Ffd%2Fauth%2Fsignin%3Faction%3Dfacebook_oauth%26provider%3Dfacebook&api_key=111239619098")
    driver.find_element_by_xpath('//*[@id="email"]').send_keys(args.username);
    driver.find_element_by_xpath('//*[@id="pass"]').send_keys(args.password);
    driver.find_element_by_xpath('//*[@id="u_0_1"]').click()

elif args.login == "ms":
    driver.get("https://login.live.com/login.srf?wa=wsignin1.0&rpsnv=11&ct=1367638624&rver=6.0.5286.0&wp=MBI&wreply=http:%2F%2Fwww.bing.com%2FPassport.aspx%3Frequrl%3Dhttp%253a%252f%252fwww.bing.com%252f&lc=1033&id=264960")
    driver.find_element_by_xpath('//*[@id="i0116"]').send_keys(args.username);
    driver.find_element_by_xpath('//*[@id="i0118"]').send_keys(args.password);
    driver.find_element_by_xpath('//*[@id="idSIButton9"]').click()

# run searches
login = True;
try:
    driver.find_element_by_xpath('//*[@id="sb_form_q"]').send_keys("start")
    driver.find_element_by_xpath('//*[@id="sb_form_go"]').click()
    print 'login successful to ' + args.login
except:
    print 'login failed' 
    login = False

if login:
    for i in range(args.numsearch):
        search_bar = driver.find_element_by_xpath('//*[@id="sb_form_q"]')
        search_button = driver.find_element_by_xpath('//*[@id="sb_form_go"]')
        search_string = generate_search()
        search_bar.clear()
        search_bar.send_keys(search_string)
        search_button.click()

    # get bonus rewards
    print 'getting bonus rewards'
    driver.get('http://www.bing.com/rewards/dashboard')
    mylist = driver.find_elements_by_xpath("//*[contains(@href,'rewardsapp')]")
    numlinks = len(mylist)

    first = 0
    if 'Connect to Facebook' in mylist[first].text:
        first = 1

    for i in range(numlinks):
        try:
            mylist[first].click()
        except:
            print "couldn't click element"

        driver.get('http://www.bing.com/rewards/dashboard')
        mylist = driver.find_elements_by_xpath("//*[contains(@href,'rewardsapp')]")



# stop virtual display
if args.virtual:
    display.stop()

driver.quit()
try:
    os.remove("chromedriver.log")
    os.remove("libpeerconnection.log")
except:
    print "logs don't exist or failed to remove"
