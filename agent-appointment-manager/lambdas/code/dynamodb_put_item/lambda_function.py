###############################################################
## This function is to populate a dynamoDB table with a CSV ###
###############################################################

import json
import csv
import boto3
import os
import time

BASE_PATH = '/tmp/'
CSV_SEPARATOR = ';'

ddb = boto3.resource('dynamodb')
table = ddb.Table(os.environ['TABLE_NAME'])


def save_item_ddb(table,item):
    response = table.put_item(Item=item)
    return response


def lambda_handler(event, contex):
    agent = event['agent']
    actionGroup = event['actionGroup']
    function = event['function']
    parameters = event.get('parameters', [])

    # Execute your business logic here. For more information, refer to: https://docs.aws.amazon.com/bedrock/latest/userguide/agents-lambda.html
    
    item_value = {}

    for n in parameters:
        print(n)
        item = n["name"]
        item_value[item] = n["value"]
        
    print(item_value)
        
    #item_value = json.loads(item)
    item_value["phone_number"] = item_value["phone_number"].replace("+","")
    
    response = save_item_ddb(table,item_value)
    print(response)
    
    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
        responseBody =  {
                "TEXT": {
                    "body": "The function {} was called successfully!".format(function)
                }
            }
    else:
        responseBody =  {
                "TEXT": {
                    "body": "The function {} with error!".format(function)
                }
                }
            
    

    action_response = {
        'actionGroup': actionGroup,
        'function': function,
        'functionResponse': {
            'responseBody': responseBody
        }

    }
    
    dummy_function_response = {'response': action_response, 'messageVersion': event['messageVersion']}
    print("Response: {}".format(dummy_function_response))

    return dummy_function_response
    