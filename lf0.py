import json
import boto3

def lambda_handler(event, context):

   

    client = boto3.client('lex-runtime')
    response = client.post_text(
        botName='bot',
        botAlias='chatbot',
        userId='100',
        sessionAttributes={
            },
        requestAttributes={
        },
        inputText = event['messages'][0]['unstructured']['text']
    )
    print("Message from bot:" +response["message"])
    return {
        'statusCode': 200,
        'body': json.dumps(response["message"])
    }