import boto3
import json
import os
from boto3.dynamodb.conditions import Key

def lambda_handler(event, context):
    # DynamoDB setup
    dynamodb = boto3.resource('dynamodb')

    table_name = 'Inventory'


    # Get the Id from the path parameters
    if 'pathParameters' not in event or 'id' not in event['pathParameters']:
        return {
            'statusCode': 400,
            'body': json.dumps("Missing 'id' path parameter")
        }

    key_value = event['pathParameters']['id']

    # Query using PK only (Id) instead of get_item
    try:
        response = table.query(
            KeyConditionExpression=Key('Id').eq(key_value)
        )
        items = response.get('Items', [])

        if not items:
            return {
                'statusCode': 404,
                'body': json.dumps('Item not found')
            }

        return {
            'statusCode': 200,
            'body': json.dumps(items, default=str)
        }
    except Exception as e:
        print(e)
        return {
            'statusCode': 500,
            'body': json.dumps(str(e))
        }