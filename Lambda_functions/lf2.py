
import json
import boto3
from botocore.vendored import requests
from boto3.dynamodb.conditions import Key, Attr
import logging

import os
import botocore.credentials
from botocore.awsrequest import AWSRequest
from botocore.httpsession import URLLib3Session
from botocore.auth import SigV4Auth
import random
#logger = logging.getLogger()
#logger.setLevel(logging.DEBUG)



def lambda_handler(event, context):

    sqs = boto3.client('sqs')
    response = sqs.get_queue_url(QueueName='bot')
    queue_url = response['QueueUrl']
    print(queue_url)
    message = None
    response = sqs.receive_message(
        QueueUrl=queue_url,
        AttributeNames=[
            'SentTimestamp'
        ],
        MaxNumberOfMessages=1,
        MessageAttributeNames=[
            'All'
        ],
        VisibilityTimeout=0,
        WaitTimeSeconds=0
    )
    try:
        message = response['Messages'][0]
        receipt_handle = message['ReceiptHandle']
       
        sqs.delete_message(
            QueueUrl=queue_url,
            ReceiptHandle=receipt_handle
        )
        print('Received and deleted message: %s' % message)
       
        location = message['MessageAttributes']['location']['StringValue']
        cuisine = message['MessageAttributes']['cuisine']['StringValue']
        dining_date =  message['MessageAttributes']['dining_date']['StringValue']
        dining_time = message['MessageAttributes']['dining_time']['StringValue']
        num_people = message['MessageAttributes']['num_people']['StringValue']
        phone =  message['MessageAttributes']['phone']['StringValue']
       
        sendMessage = None
       
       
        headers = {
        'Host': 'search-restaurant-2talfnqdstlylxyh2czpqf6zre.us-east-1.es.amazonaws.com',
        }
        request = AWSRequest(method="GET", url='https://search-restaurant-2talfnqdstlylxyh2czpqf6zre.us-east-1.es.amazonaws.com/restaurants/_search?q='+str(cuisine),headers=headers)
        SigV4Auth(boto3.Session().get_credentials(), "es", "us-east-1").add_auth(request)    


        session = URLLib3Session()
        r = session.send(request.prepare())
        #r = requests.get('https://search-restaurants-gt6ebxvhorvxtr5osyn2th2vzy.us-east-1.es.amazonaws.com/restaurants/_search?q='+str(cuisine))
        txt=r.text
        
        
       
        print(txt)
        print(r)
        d=json.loads(txt)
        #print(phone)
        print(d)
        print(len(d['hits']['hits']))
        index=random.randint(0,len(d['hits']['hits'])-3)
        dynamodb = boto3.resource('dynamodb')
        recommend=''
        for i in range(3):
            bid = d['hits']['hits'][index]['_source']['bid']
            print(bid)
           
            #print(response)
           
            
            table = dynamodb.Table('yelp-restaurants')
            response = table.query(
                KeyConditionExpression=Key('bid').eq(bid)
            )
            #print(response)
            name = response['Items'][0]['name']
            address = response['Items'][0]['Address']
            num_reviews = response['Items'][0]['nreviews']
            rating = response['Items'][0]['rating']
            newmsg="{}.We recommend {}, which serves {} food, on {}. The place has {} of reviews and an average score of {} on Yelp.\n".format(i+1, name, cuisine, address, num_reviews, rating)
            recommend=recommend+newmsg
            index+=1
        sendMessage = "Hello!These are the recommendations for {} cuisine in {}\n".format(cuisine,location)
        final_message= sendMessage + recommend + "Thanks for using our service we hope you enjoy your meal!"
        sns=boto3.client('sns')
        response=sns.publish(
            PhoneNumber = '+1'+phone,
            Message = final_message
        )
        
        print(response)
    except:
        print("SQS queue is now empty")

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda LF2!')
    }