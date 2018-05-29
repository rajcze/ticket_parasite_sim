# Ticket parasite simulation

## Synopsis

With this project I do not prompt anyone to gamble! This is just an experiment to simulate betting process and to find out IF is really possible gain profit.
How it works?
This script continuously checks unspecified (to avoid attention from this service, site name is hidden and can be found in simulation.py) site for tipsters IDs.
After that each found tipster is checked for two relevant values: ROI and noA
ROI - return of investment (like 0.1 or 0.2). This means -> tipster started with $1000 and now his balance is $1001 (if ROI is 0.1(%))
noA - number of analyzes -> if tipster writes and is publishing analyzes, we can state fact that he understands why he is making certain bet and isn't just gambling
These two filters return list of trustworthy tipsters. What next?
Every single one tipster from list above is checked for last analyzes he made and every analysis is checked for all tickets connected to it.
Now, if there is "fresh" ticket (means is not evaluated and is possible to make a bet), simulation saves this ticket into "/found_tickets" and deducts ref_moneyin (variable by default set to 1000) from budget(balance).
That's how is betting simulated.
Last part of script is evaluation. Script checks all tickets from "/found_tickets" and compares with online live version of ticket. 
If ticket is found to be evaluated - and won: it's moved to "/finished_W" and balance is raised by ref_moneyin*rate (rate is winning ratio specified by ticket)
If ticket is found to be evaluated - and lost: it's moved to "/finished_W" and balance is left unchanged (money were already deducted)

## Installation
```bash
git clone https://github.com/kouzelnikCZ/ticket_parasite_sim
cd ticket_parasite_sim
./install.sh
```
At this moment your setup is ready. Budget for simulation is set by default to 30k.

## Run simulation
```bash
someone@something:~/ticket_parasite_sim$
python simulation.py myemail@somewhere.net MySecretPassword
```
Your simulation should be running now until you stop it with CTRL+C. Highly recommended is to open reader for data from simulation in another terminal window:
```bash
someone@something:~/ticket_parasite_sim$
python plot_data.py <args>
```
Reader has 3 argument that specify what to read.
```bash
someone@something:~/ticket_parasite_sim$
python plot_data.py               #shows only budget change time and budget value
python plot_data.py show_all      #shows like previous + number of invested tickets, number of profitable and lossy and net profit* 
python plot_data.py date          #shows date and time when invested tickets will be evaluated
```
*net profit -> fake account balance + ref_moneyin * number of invested tickets
