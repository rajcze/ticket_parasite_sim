# -*- coding: utf-8 -*-
#Author: @kouzelnikCZ

import sys
import pickle

def save_obj(obj, name, folder):
	with open(folder + '/'+ name + '.pkl', 'wb') as f:
		pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

def load_obj(name, folder):
	with open(folder + '/' + name + '.pkl', 'rb') as f:
		return pickle.load(f)

if len(sys.argv) == 1:
	investment = 30000.0
else:
	try:
		investment = float(sys.argv[1])
	except:
		raise ValueError("Input value must be int or float!")

print "Budget set to " + str(investment)
save_obj(investment,"investment","variables")