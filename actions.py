# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
import requests
import json

from rasa_core_sdk import Action
from rasa_core_sdk.events import SlotSet

logger = logging.getLogger(__name__)

class ActionRestaurantSearch(Action):
	def name(self):
	# define the name of the action which can then be included in training stories
		return 'action_restaurant_search'


	def get_location(self, location):
		req_url = "https://api.opencagedata.com/geocode/v1/json?q="+location+"&key=% API %"
		res = requests.get(req_url)

		latitude, longitude = "40.789623", "-73.9598939"

		if res.status_code == 200:
			loc = res.json()['results'][0]['annotations']['DMS']
			lat = loc['lat'].split()
			latitude = float(lat[0][:-1]) + float(lat[1][:-1])/60 + float(lat[2][:-2])/3600
			if lat[-1] == "S":
				latitude = - latitude
			longi = loc['lng'].split()
			longitude = float(longi[0][:-1]) + float(longi[1][:-1])/60 + float(longi[2][:-2])/3600
			if longi[-1] == "W":
				longitude = - longitude

		return str(round(latitude,6)), str(round(longitude,6))


	def run(self, dispatcher, tracker, domain):
		# what your action should do
		location = tracker.get_slot('location') or 'gurgoan'
		cuisine = tracker.get_slot('cuisine') or 'north indian'

		dispatcher.utter_message(location+cuisine)

		latitude, longitude = self.get_location(location)

		url = "https://us-restaurant-menus.p.rapidapi.com/restaurants/search/geo"

		querystring = {"lon":longitude+"\t","lat":latitude,"distance":"10","page":"1"}

		headers = {
			'RapidAPI App': "default-application_5106530",
    		'x-rapidapi-key': "% API %",
    		'x-rapidapi-host': "us-restaurant-menus.p.rapidapi.com"
    	}

		response = requests.request("GET", url, headers=headers, params=querystring)
		try:
			response = response.json()
			if int(response["result"]["totalResults"]) > 0:
				for rest in response['result']['data']:
					menu = rest['cuisines'] 
					menu = [ c.lower() for c in menu]
					if cuisine in menu:
						dispatcher.utter_message("NAME: " + rest['restaurant_name'])
						dispatcher.utter_message("CUISINES: " + str(rest['cuisines']))
						dispatcher.utter_message("ADDRESS: " + rest['address']['formatted'])
						dispatcher.utter_message("COST: " + rest['price_range'])
			else:
				dispatcher.utter_message("NO RESTAURANTS")
		except:
			dispatcher.utter_message("ERROR")
		return []