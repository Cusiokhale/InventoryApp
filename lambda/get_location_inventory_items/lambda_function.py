import json
import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
from decimal import Decimal
import os

# Initialize DynamoDB resource
dynamodb = boto3.resource('dynamodb')

# Table and index names
TABLE_NAME = os.getenv('TABLE_NAME', 'Inventory')  
GSI_NAME = 'locationInventoryItems'                

# Function to convert Decimal to int/float for JSON
def convert_decimals(obj):
    if isinstance(obj, list):
        return [convert_decimals(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: convert_decimals(v) for k, v in obj.items()}
    elif isinstance(obj, Decimal):
        return int(obj) if obj % 1 == 0 else float(obj)
    return obj

def lambda_handler(event, context):
    table = dynamodb.Table(TABLE_NAME)

    # Validate path parameter
    path_params = event.get('pathParameters') or {}
    if 'id' not in path_params:
        return {
            'statusCode': 400,
            'body': json.dumps("Missing 'id' path parameter")
        }

    # location_id from path 
    try:
        location_id = (path_params['id'])  
    except ValueError:
        return {
            'statusCode': 400,
            'body': json.dumps("Path parameter 'id' must be valid")
        }

    try:
        # Query the GSI to get all inventory items for this location
        response = table.query(
            IndexName=GSI_NAME,
            KeyConditionExpression=Key('location_id').eq(location_id)
        )

        items = response.get('Items', [])
        items = convert_decimals(items)

        return {
            'statusCode': 200,
            'body': json.dumps(items)
        }

    except ClientError as e:
        print(f"Failed to query items: {e.response['Error']['Message']}")
        return {
            'statusCode': 500,
            'body': json.dumps('Failed to query items')
        }
