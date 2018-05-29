#!/usr/bin/env bash
#author: @kouzelnikCZ

rm -rf variables
mkdir -p variables/finished_L
mkdir -p variables/finished_W
mkdir -p variables/found_tickets
mkdir -p variables/txt_invs
python setInvest.py
