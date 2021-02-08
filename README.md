# Concierge Chatbot Service on AWS

Project 01 of the Cloud Computing & Big Data Course at NYU taught by Prof. [Sambit Sahu](https://engineering.nyu.edu/sambit-sahu) 

The aim of the project is to implement a serverless, microservice-driven web application. 

The Chatbot service provides restaurant suggestions based on cuisine preferences given to the chatbot through conversation. 

Tools & AWS Services Used: [API Gateway](https://aws.amazon.com/api-gateway/), [DynamoDB](https://aws.amazon.com/dynamodb/), [ElasticSearch](https://aws.amazon.com/elasticsearch-service/), [Lambda](https://aws.amazon.com/lambda/), [Lex](https://aws.amazon.com/lex/), [S3](https://aws.amazon.com/s3/), [SQS](https://aws.amazon.com/sqs/), [SNS](https://aws.amazon.com/sns/), [Swagger](https://swagger.io/), [Yelp Developer API](https://www.yelp.com/developers)  


## System Architecture & Workflow

<p align="center">
  <img src="https://github.com/Dhuldhoyavarun/concierge-chatbot/blob/main/Lambda_functions/Architecture.PNG" width='700' title="Architecture">
</p>

+ The DynamoDB database is used to store restaurant information scraped using the YelpAPI. Necessary recommendation information such as Business ID, Name, Address, Coordinates,
Number of Reviews, Rating, Zip Code of the restaurants is stored in the database. 

+ The ElasticSearch instance stores partial information for each restaurant scraped in ElasticSearch wherein each entry has a 'Restaurant' data type and only the BusinessId & Cuisine are stored for each restaurant.

+ Front-End of the application is deployed on the S3 bucket which is set up for web hosting. A Front-end starter application provided by the Professor and found in [this](https://github.com/ndrppnc/cloud-hw1-starter) repository is repurposed to interface with the Chatbot.

+ The given [API specification](https://github.com/001000001/aics-columbia-s2018/blob/master/aics-swagger.yaml) is imported into the API Gateway which generates an SDK that is used in the front-end of the application. 

+ The Lambda Function 'LF0' performs the chat operation. This function is used as a request-response entity between the Lex Chatbot and the SDK. 

+ The Lambda Function 'LF1' is used as a code hook for the Lex chatbot. This is used for manipulating as well as validating request parameters and formatting bot responses. Three intents are implemented in the Chatbot, GreetingIntent, ThankYouIntent and DiningSuggestionIntent. The information parsed from the request is pushed to an SQS queue.

+ The Lambda Function 'LF2' acts as a queue worker which is triggered every minute by a CloudWatch trigger. This function pulls messages from the SQS queue, gets a random restaurant recommendation for the cuisine collected through conversation from ElasticSearch and DynamoDB, formats the recommendation and sends it to the user's phone number obtained from the SQS queue using SNS.    

