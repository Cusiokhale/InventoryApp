import boto3
import json
from boto3.dynamodb.conditions import Key
import os

dynamodb = boto3.resource('dynamodb')
TABLE_NAME = os.getenv('TABLE_NAME', 'Inventory')  # default table name
table = dynamodb.Table(TABLE_NAME)

def lambda_handler(event, context):
    # Validate path parameter
    path_params = event.get('pathParameters') or {}
    key_value = path_params.get('id')

    if not key_value:
        return {
            'statusCode': 400,
            'body': json.dumps("Missing 'id' path parameter")
        }

    try:
        # Query using PK (Id)
        response = table.query(
            KeyConditionExpression=Key('Id').eq(key_value)
        )
        items = response.get('Items', [])

        if not items:
            return {
                'statusCode': 404,
                'body': json.dumps('Item not found')
            }

        # Delete each item using full PK + SK
        for item in items:
            table.delete_item(
                Key={
                    'id': item['id'],                   # PK
                    'location_id': item['location_id']   # SK
                }
            )

        return {
            'statusCode': 200,
            'body': json.dumps(f"Item with ID {key_value} deleted successfully.")
        }

    except Exception as e:
        print(e)
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error deleting item: {str(e)}")
        }
