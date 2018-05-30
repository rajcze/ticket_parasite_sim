# -*- coding: utf-8 -*-
#Author: @kouzelnikCZ

import re
import sys
import os
import pickle
import requests
from time import sleep
from random import uniform
import datetime

#fast way to save variables via pickle
def save_obj(obj, name, folder):
	with open(folder + '/'+ name + '.pkl', 'wb') as f:
		pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

#fase way to load variables via pickle
def load_obj(name, folder):
	with open(folder + '/' + name + '.pkl', 'rb') as f:
		return pickle.load(f)

#formated timestamp for saving continuous results
def timestamp():
	return str(datetime.datetime.now().strftime('%Y-%m-%d-%H-%M'))

#formats dateclose variable from web to datetime
def enddate(dateclose):
	datecloseList = dateclose.split("-")
	formated = datetime.datetime(int(datecloseList[2]),int(datecloseList[1]),int(datecloseList[0]),int(datecloseList[3]),int(datecloseList[4]))
	return formated

#debug argument and default variables
args = sys.argv
try:
	if args[5] == "--debug":
		debug = True
except:
	debug = False

try:
	ref_ROI = float(args[3])
except:
	ref_ROI = 0.15				#return of investment - shows how successful bookmaker ("tipster") is

try:
	ref_noA = int(args[4])
except:
	ref_noA = 45				#number of analyzes - shows how many analyzes tipster made so far

ref_moneyin = 1000			#value to bet
ref_days = 21				#reffers to how many days forward can script bet
user_limiter = 50			# if debug, only this amount of tipsters will be checked 

#login credentials from arguments
payload = {
	'userName': args[1],
	'password': args[2]
}

#infinite loop
while True:
	#session creation for one simulation step
	with requests.Session() as s:
		print "Starting simulation step:"
		investment = load_obj("investment","variables")
		print "Simulation account balance: " + str(investment)
		with open("variables/txt_invs/" + timestamp() + ".txt","w+") as f:
			f.write(str(investment))
		print "logging to web"
		# Using 'with' to ensure the session context is closed after use.

		#initializing counter of relevant tipsters
		users_found = 0

		try:
			p = s.post('https://www.tipsport.cz/LoginAction.do', data=payload)
		except:
			print "Connection error, trying again in one minute"
			sleep(60)

		#An authorised request.
		print "Logged in"

		#looking for tipsters writing analyzes
		r = s.get('https://www.tipsport.cz/analyzy#=nap%C5%99.%20fotbal&startTime=0&rateFrom=&rateTo=&show=ALL&author=&sort=INSPIRATIONS&firm=&matchName=&pageNumber=1')
		users_query = re.findall(r"<a href=\"/ViewClientProfileAction\.do\?pId=(.*?)%3D%3D", r.text.encode("utf-8")) 
		
		#merging users_query with one from previous simulation steps (if there are any)
		if (os.path.isfile("variables/users_query.pkl")):
			old_users_query = load_obj("users_query","variables")
			users_query = users_query + old_users_query
			users_query = set(users_query)
			users_query = list(users_query)
			save_obj(users_query,"users_query","variables")
			print "users_query is found, merging"
		else:
			users_query = set(users_query)
			users_query = list(users_query)
			save_obj(users_query,"users_query","variables")
			print "users_query not found, creating new"

		#F1 - filter 1 -> comparing tipsters ROI with referral ROI
		print "Starting filter 1 by ref_ROI: " + str(ref_ROI)
		print "for users_query: " + str(len(users_query))

		accs_for_analyzes = []
		#number of found relevant tipsters with filter 1
		number = 0

		for user in users_query:
			#user profile
			url = "https://www.tipsport.cz/ViewClientProfileAction.do?pId=" + user + "%3D%3D&countryId=1&section=analyzes"
			u = s.get(url)
			print url
			ROI = re.findall(r"\s(.*?)<span>ROI</span>", u.text.encode("utf-8"))
			#if there is no ROI found, ROI will be set to zero and wont proceed through filter
			if len(ROI) < 1:
				ROI = "0%"
			else:
				ROI = ROI[0]
			ROI = float(ROI.replace("%",""))
			#if user is relevant by filter 1
			if ROI >= ref_ROI:
				number += 1
				print "F1: found relevant tipster n." + str(number)
				accs_for_analyzes.append(user)
			users_found += 1
			if (debug) and (users_found >= user_limiter):
				break

		print "F1 finished for: " + str(len(users_query)) + "	||	filtered to: " + str(len(accs_for_analyzes))

		#F2 - filter 2 -> comparing tipsters number of analyzes with referral noA
		print "Starting filter 2 by ref_noA: " + str(ref_noA)
		#number of found relevant tipsters with filter 2
		number_2 = 0
		#creating empty list for users ID (only relevant tipsters)
		accs_for_analyzes_2nd = []

		for user in accs_for_analyzes:
			url = "https://www.tipsport.cz/ViewClientProfileAction.do?pId=" + user + "%3D%3D&countryId=1&section=analyzes"
			u = s.get(url)
			print url
			noA = re.findall(r"\s(.*?)<span>zveřejněných analýz</span>", u.text.encode("utf-8"))
			#if there is no number of analyzes found, noA set to zero and wont proceed through filter
			if len(noA) < 1:
				noA = "0"
			else:
				noA = noA[0]
			noA = float(noA)
			#if user is relevant by filter 2
			if noA >= ref_noA:
				number_2 += 1
				print "F2: found relevant tipster n." + str(number_2)
				accs_for_analyzes_2nd.append(user)
		print "F2 is finished, relevant tipsters: " + str(len(accs_for_analyzes_2nd))

		#creating empty list for found tickets for further bet
		analyzes = []
		for user in accs_for_analyzes_2nd:
			url = "https://www.tipsport.cz/ViewClientProfileAction.do?pId=" + user + "%3D%3D&countryId=1&section=analyzes"
			u = s.get(url)
			users_analyzes = re.findall(r"Commons\.openAnalyze\('/ViewAnalyzeDetailAction\.do\?aId=(.*?)'", u.text.encode("utf-8"))
			print "Looking for analyzes by " + url
			# looking for users analyzes
			for users_ana in users_analyzes:
				url = "https://www.tipsport.cz/ViewAnalyzeDetailAction.do?aId=" + users_ana
				u = s.get(url)
				tickets = re.findall(r"data-tlink=\"(.*?)\">", u.text.encode("utf-8"))
				print ">> analysis found, looking for tickets"
				#loads analysis and looks for tickets
				for ticket in tickets:
					ticket = ticket.split(":")
					ticketUrl = "https://www.tipsport.cz/tiket?idu=" + ticket[0] + "&idb=" + ticket[1] + "&hash=" + ticket[2]
					#saving ticket url
					analyzes.append(ticketUrl)
					print ">>>> ticket found, added to ticket list:"
					print ticketUrl

		print "Total number of tickets to be checked: " + str(len(analyzes))

		#number of invested tickets this step
		inv_tickets = 0
		for ticketUrl in analyzes:
			print "Processing ticket:"
			ticketId = re.findall(r"tiket\?idu=(.*?)&idb", ticketUrl)[0]
			print ticketUrl
			t = s.get(ticketUrl)

			#scrapping data from ticket

			#date and time when match takes place
			dateclose = re.findall(r"<span class=\"tDateClose\">(\s.*?)</span>", t.text.encode("utf-8"))
			if len(dateclose) > 0:
				dateclose = dateclose[0]
				dateclose = dateclose.replace(" ","-")
				dateclose = dateclose.replace(".","-")
				dateclose = dateclose.replace(":","-")
				dateclose = dateclose.replace("\n","")
				dateclose = dateclose.replace("--","")
				dateclose = enddate(dateclose)
			#system number of opportunity (if wins A, if wins B, if deuce...)
			oppNum = re.findall(r"oppNum\">(.*?)</span>", t.text.encode("utf-8"))
			if len(oppNum) > 0:
				oppNum = oppNum[0]
				oppNum = oppNum.replace("\n","")
				oppNum = oppNum.replace(" ","")
				oppNum = oppNum.replace("&nbsp;","")
			#money invested by tipster
			moneyIn = re.findall(r"<td class=\"colLast noWrap\">(\s.*?)&nbsp;Kč</td>", t.text.encode("utf-8"))
			if len(moneyIn) > 0:
				moneyIn = moneyIn[0]
				moneyIn = moneyIn.replace(" ","")
				moneyIn = moneyIn.replace("\n","")
				moneyIn = float(moneyIn.replace(",","."))
			#winning ratio 
			rate = re.findall(r"<td class=\"colOdd\">(\s.*?)</td>", t.text.encode("utf-8"))
			if len(rate) > 0:
				rate = rate[0]
				rate = rate.replace(" ","")
				rate = float(rate.replace("\n",""))
			#system matchID
			matchID = re.findall(r"<strong data-m=\"(.*?)\"", t.text.encode("utf-8"))

			#lot of ifs to make sure ticket is relevant and worthy to bet (or is not somehow broken by system)
			if len(matchID) > 0:
				matchID = matchID[0]
			#status of the ticket .. if is evaluated
			status = re.findall(r"<span class=\"hideScreen\">(.*?)</span>", t.text.encode("utf-8"))
			if len(status) > 0:
				status = status[0]
			if isinstance(oppNum,(str,)) and isinstance(dateclose,(datetime.datetime,)) and isinstance(moneyIn,(float,)) and isinstance(rate,(float,)) and isinstance(matchID,(str,)) and isinstance(status,(str,)):
				if (matchID != "0") and (status == "nevyhodnoceno"):
					if not (os.path.isfile("variables/found_tickets/" + ticketId + ".pkl")):
						if ((dateclose-datetime.datetime.now()).days < ref_days) and ((dateclose-datetime.datetime.now()).days >= 0):
							#creating ticket variable which will be saved with save_obj
							found_ticket = {
								"url":ticketUrl,
								"oppNum":oppNum,
								"moneyIn":moneyIn,
								"rate":rate,
								"matchID":matchID,
								"status": status,
								"dateclose": dateclose
								}
							inv_tickets += 1
							save_obj(found_ticket,ticketId,"variables/found_tickets")
							investment = load_obj("investment","variables")
							changed_investment = investment - ref_moneyin
							save_obj(changed_investment,"investment","variables")
							print found_ticket
							print investment
							print changed_investment

		print "Catching of new tickets is finished"
		print "Proceeding to check old ones"
		#counters for winning or loosing tickets
		ticket_counterW = 0
		ticket_counterL = 0
		print "Number of tickets to be checked: " + str(len(os.listdir('variables/found_tickets')))
		for ticketId in os.listdir('variables/found_tickets'):
			ticketId = ticketId[:-4]
			folder = "variables/found_tickets"
			ticket = load_obj(ticketId,folder)

			if ticket["status"] == "nevyhodnoceno":
				print ">>checking non evaluated ticket"
				tn = s.get(ticket["url"])
				status = re.findall(r"<span class=\"hideScreen\">(.*?)</span>", tn.text.encode("utf-8"))[0]
				#changing ticket status
				ticket["status"] = status

			#if ticket is won
			if ticket["status"] == "výhra":
				name = ticketId + ".pkl"
				os.remove("variables/found_tickets/" + name)
				save_obj(ticket,ticketId,"variables/finished_W")
				investment = load_obj("investment","variables")
				changed_investment = investment + ref_moneyin*ticket["rate"]
				ticket_counterW += 1
				print ">>>> vyhraný tiket:"
				print "changed_investment:"
				print changed_investment
				save_obj(changed_investment,"investment","variables")

			#if ticket is lost
			if ticket["status"] == "prohra":
				name = ticketId + ".pkl"
				os.remove("variables/found_tickets/" + name)
				save_obj(ticket,ticketId,"variables/finished_L")
				ticket_counterL += 1
				print ">>>> prohraný tiket za:"
				print ref_moneyin
			#if ticket is still not evaluated
			if ticket["status"] == "nevyhodnoceno":
				print ">>>> no change"

	print "<= Invested tickets: " + str(inv_tickets)
	print "=> Profitable tickets: " + str(ticket_counterW)
	print "=>!!! Lossy tickets: " + str(ticket_counterL)
	print "Simulation step is finished, fake account balance is:"
	investment = load_obj("investment","variables")
	with open("variables/inv_now.txt","w+") as f:
		f.write(str(investment))
	print investment
	time = uniform(3.0, 10.0)*60
	print "... next step in: " + str(time/60) + " minutes"
	sleep(time)