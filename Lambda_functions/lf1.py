
from __future__ import print_function
import time
import os
import logging
import dateutil.parser
import math
import boto3
import json


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
def get_slots(req):
    return req['currentIntent']['slots']

def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit, message):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'ElicitSlot',
            'intentName': intent_name,
            'slots': slots,
            'slotToElicit': slot_to_elicit,
            'message': message
        }
    }

def close(session_attributes, fulfillment_state, message):
    response = {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': fulfillment_state,
            'message': message
        }
    }
    return response

def delegate(session_attributes, slots):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Delegate',
            'slots': slots
        }
    }


def try_ex(func):
  
    try:
        return func()
    except KeyError:
        return None

def parse_int(n):
    try:
        return int(n)
    except ValueError:
        return float('nan')

def safe_int(n):
  
    if n is not None:
        return int(n)
    return n

def validate(is_valid, violated_slot, message_content):
    if message_content is None:
        return {
            "isValid": is_valid,
            "violatedSlot": violated_slot,
        }

    return {
        'isValid': is_valid,
        'violatedSlot': violated_slot,
        'message': {'contentType': 'PlainText', 'content': message_content}
    }

def isvalid_date(date):
    try:
        dateutil.parser.parse(date)
        return True
    except ValueError:
        return False

def validate_dining(slots):
    location = slots['location']
    cuisine = slots['cuisine']
    dining_date = slots['date']
    dining_time = slots['time']
    num_people = safe_int(slots['no_people'])
    logger.debug('location={}'.format(location))
    valid_cities = ['new york']
    if location is not None and location.lower() not in valid_cities:
        return validate (False,'location','Sorry that currently {} is not a valid destination. Could you try a different city?'.format(location))

    if dining_date is not None:
        if not isvalid_date(dining_date):
            return validate(False, 'date', 'I did not understand that, what date would you like to have the cuisine?')

    if dining_time is not None:
        if len(dining_time) != 5:
            return validate(False, 'time', 'I am sorry that it is not a valid time. Please enter a valid time.')
        hour, minute = dining_time.split(':')
        hour = parse_int(hour)
        minute = parse_int(minute)
        if math.isnan(hour) or math.isnan(minute):
            return validate(False, 'time', 'I am sorry that it is not a valid time. Please enter a valid time.')
        if hour < 0 or hour > 24:
            return validate(False, 'time', 'I am sorry that it is not a valid time. Please enter a valid time.')
    
    if num_people is not None and (num_people < 1):
        return validate(
            False,
            'no_people',
            'The minimum number of people is 1. How many people do you have?'
        )

    return {'isValid': True}


def dining(req):

    location = req['currentIntent']['slots']['location']
    cuisine = req['currentIntent']['slots']['cuisine']
    dining_date =  req['currentIntent']['slots']['date']    
    dining_time = req['currentIntent']['slots']['time']
    num_people = safe_int(req['currentIntent']['slots']['no_people'])
    phone = req['currentIntent']['slots']['phoneno']
   
    if req['invocationSource'] == 'DialogCodeHook':
        
        validation_result = validate_dining(req['currentIntent']['slots'])
        
        if not validation_result['isValid']:
            
            slots = req['currentIntent']['slots']
            slots[validation_result['violatedSlot']] = None
            
            return elicit_slot(
                req['sessionAttributes'],
                req['currentIntent']['name'],
                slots,
                validation_result['violatedSlot'],
                validation_result['message']
            )
        session_attributes = req['sessionAttributes'] if req['sessionAttributes'] is not None else {}
        return delegate(session_attributes, get_slots(req))
    elif req['invocationSource'] == 'FulfillmentCodeHook':
       
        sqs = boto3.client('sqs')

        response = sqs.get_queue_url(QueueName='bot')
        queue_url = response['QueueUrl']
        print(queue_url)
        print(location, cuisine, dining_date, dining_time, num_people, phone)
      
        response = sqs.send_message(
            QueueUrl=queue_url,
            MessageAttributes={
                'location': {
                    'DataType': 'String',
                    'StringValue': location
                },
                'cuisine': {
                    'DataType': 'String',
                    'StringValue': cuisine
                },
                'dining_date': {
                    'DataType': 'String',
                    'StringValue': dining_date
                },
                'dining_time': {
                    'DataType': 'String',
                    'StringValue': dining_time
                },
                'num_people': {
                    'DataType': 'Number',
                    'StringValue': str(num_people)
                },
                'phone': {
                    'DataType': 'String',
                    'StringValue': str(phone)
                }
            },
            MessageBody=(
                'Information about user inputs of Dining Chatbot.'
            )
        )
        print("SQS messageID:"+str(response['MessageId']))
       
        res_msg = "Thanks for your information. Our recommendation will be sent to your phone shortly!"
        
        return close(req['sessionAttributes'],
                    'Fulfilled',
                    {'contentType': 'PlainText',
                    'content': res_msg})

def grt(req):
    session_attributes = req['sessionAttributes'] if req['sessionAttributes'] is not None else {}
    return close(
        session_attributes,
        'Fulfilled',
        {
            'contentType': 'PlainText',
            'content': 'Hi there, how can I help you?'
        }
    )

def ty(req):
    session_attributes = intent_request['sessionAttributes'] if re['sessionAttributes'] is not None else {}
    return close(
        session_attributes,
        'Fulfilled',
        {
            'contentType': 'PlainText',
            'content': 'You are welcome! Thanks for using the service. See you next time!'
        }
    )


def execute(req):
   
    logger.debug('dispatch userId={}, intentName={}'.format(req['userId'], req['currentIntent']['name']))
    intent= req['currentIntent']['name']

    if intent == 'greetingintent':
        return grt(req)
    elif intent == "diningintent":
        return dining(req)
    elif intent == "thankyouintent":
        return ty(req)
    raise Exception('Intent with name ' + intent + ' not supported')


def lambda_handler(event, context):
    
    os.environ['TZ'] = 'America/New_York'
    time.tzset()
    logger.debug('event.bot.name={}'.format(event['bot']['name']))
    return execute(event)