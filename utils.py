import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "newsbot-clidny-5379eb78f060.json"

import dialogflow_v2 as dialogflow
dialogflow_session_client = dialogflow.SessionsClient()
PROJECT_ID = "newsbot-clidny"

import json
import requests

from gnewsclient import gnewsclient
client = gnewsclient.NewsClient(max_results=3)

import pyowm
#owm = pyowm.OWM('your key')

from pymongo import MongoClient

dBclient = MongoClient("mongo db server")
db = dBclient.get_database('chatbot')
query_record = db.requested_queries
pic_record = db.pic_info

def get_news(parameters):
	print(parameters)
	query_record.insert_one(parameters)
	client.topic = parameters.get('news_type')
	client.language = parameters.get('language')
	client.location = parameters.get('geo-country','India')
	return client.get_news()

def get_weather(parameters):
	city=parameters.get('geo-city')
	if city == '':
		lst=["Not found"]
	else :
		observation = owm.weather_at_place(city)
		w = observation.get_weather()
		wind = w.get_wind()
		temperature = w.get_temperature('celsius')
		tomorrow = pyowm.timeutils.tomorrow()
		lst=[wind,temperature]
	return lst

def detect_intent_from_text(text, session_id, language_code='en'):
    session = dialogflow_session_client.session_path(PROJECT_ID, session_id)
    text_input = dialogflow.types.TextInput(text=text, language_code=language_code)
    query_input = dialogflow.types.QueryInput(text=text_input)
    response = dialogflow_session_client.detect_intent(session=session, query_input=query_input)
    return response.query_result

def fetch_reply(msg, session_id):
	response = detect_intent_from_text(msg, session_id)
	if response.intent.display_name == 'get_news':
		news = get_news(dict(response.parameters))
		news_str = 'Here is your news:'
		for row in news:
			news_str += "\n\n{}\n\n{}\n\n".format(row['title'], row['link'])
		return ("",news_str)

	elif response.intent.display_name == 'get_weather':
		weather = get_weather( dict(response.parameters))
		weather_str = 'Here is your weather update:'
		if weather[0] == 'Not found':
			weather_str = 'Your city cannot be found !'
		else :
			wind_speed = str(weather[0]['speed'])
			wind_deg = str(weather[0]['deg'])
			temp = str(weather[1]['temp'])
			max_temp = str(weather[1]['temp_max'])
			min_temp = str(weather[1]['temp_min'])
			res = f"WIND : \n" \
				f"\tWind Speed: {wind_speed} km/hr \n" \
				f"\tWind Deg: {wind_deg} \n" \
				f"TEMPERATURE : \n" \
				f"\tTemp: {temp} °C \n" \
				f"\tMax-Temp: {max_temp} °C \n" \
				f"\tMin-Temp: {min_temp} °C \n\n"

			weather_str += res
			
			new_temp = {
				'wind_speed':wind_speed,
				'wind_deg': wind_deg,
				'temp': temp,
				'temp_min':max_temp,
				'temp_max':min_temp
				}
			query_record.insert_one(new_temp)
		return ("",weather_str)

	elif response.intent.display_name == 'get_cat':
		response = requests.get('https://aws.random.cat/meow')
		link = json.loads(response.text)
		new_pic = {'img_link':link["file"]}	#mongo structure
		pic_record.insert_one(dict(new_pic))
		return ("img",link["file"])

	else:
		return ("",response.fulfillment_text)