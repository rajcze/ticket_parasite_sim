# -*- coding: utf-8 -*-
#Author: @kouzelnikCZ

import re
import sys
import os
import pickle
import glob
import os
from time import sleep
import datetime

#argumenty spuštění
args = sys.argv
del args[0]
if ("show_all" in args) or ("--show_all" in args):
	arg_all = True
else:
	arg_all = False

if ("inv_only" in args) or ("--inv_only" in args):
	arg_inv = True
else:
	arg_inv = False

if ("date" in args) or ("--date" in args):
	date = True
else:
	date = False

def load_obj(name, folder):
	with open(folder + '/' + name + '.pkl', 'rb') as f:
		return pickle.load(f)

invest_curr = load_obj("investment","variables")
#print invest_curr
inv = 0
while True:

	search_dir = "variables/txt_invs/" 
	files = filter(os.path.isfile, glob.glob(search_dir + "*"))
	files.sort(key=lambda x: os.path.getmtime(x))
	steps_list = {}
	for step in files:
		with open(step,"r") as f:
			inv_old = inv
			inv = str(f.read())
			if inv != inv_old:
				print  step[19:-4] + " " +  inv
	if arg_all:
		noW = (len(os.listdir('variables/finished_W')))
		noL = (len(os.listdir('variables/finished_L')))
		noINV = (len(os.listdir('variables/found_tickets')))
		real_balance = (invest_curr + int(noINV)*1000) - 30000
		print "Vsazeno: " + str(noINV) + "    Ziskových: " + str(noW) + "    Ztrátových: " + str(noL) + "    Čistý Z: " + str(real_balance)
	if date:
		date_list = []
		for ticket in os.listdir('variables/found_tickets'):
			ticket_data = load_obj(ticket[:-4],'variables/found_tickets')
			date_list.append(ticket_data["dateclose"])
		date_list = sorted(date_list)
		for date in date_list:
			print date
	sleep(60)