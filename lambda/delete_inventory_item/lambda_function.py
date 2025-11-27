import boto3
import json
from boto3.dynamodb.conditions import Attr

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Inventory')

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
        # Scan the table to find the item by id
        response = table.scan(
            FilterExpression=Attr('id').eq(key_value)
        )

        items = response.get('Items', [])

        if not items:
            return {
                'statusCode': 404,
                'body': json.dumps('Item not found')
            }

        for item in items:
            table.delete_item(
                Key={
                    'location_id': item['location_id'],  # PK
                    'id': item['id']                      # SK
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