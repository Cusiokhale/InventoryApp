import json
import boto3
import os
import uuid  # using uuid4
from decimal import Decimal  

# Set up DynamoDB resource and table
dynamodb = boto3.resource('dynamodb')
TABLE_NAME = os.getenv('TABLE_NAME', 'Inventory') 
table = dynamodb.Table(TABLE_NAME)

def lambda_handler(event, context):
    # 1. Parse incoming JSON body
    try:
        body = event.get('body', '{}') 
        data = json.loads(body)
    except (TypeError, json.JSONDecodeError):
        return {
            "statusCode": 400,
            "body": json.dumps("Bad request. Please provide valid JSON in the body.")
        }

    # 2. Validate required fields
    required_fields = [
        "name",
        "description",
        "qty",
        "price",
        "location_id"
    ]

    missing = [f for f in required_fields if f not in data]
    if missing:
        return {
            "statusCode": 400,
            "body": json.dumps(f"Missing required fields: {', '.join(missing)}")
        }

    # 3. Generate ItemId using UUID4 (PK)
    item_id = str(uuid.uuid4())

    # 4. Build the DynamoDB item
    item = {
        "id": item_id,                       
        "location_id": str(data["location_id"]),  
        "name": data["name"],
        "description": data["description"],
        "qty": int(data["qty"]),
        "price": Decimal(str(data["price"])) 
    }

    # 5. Insert into DynamoDB
    try:
        table.put_item(Item=item)
        return {
            "statusCode": 200,
            "body": json.dumps(
                f"Item with ID {item_id} added successfully to location {item['LocationId']}."
            )
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps(f"Error adding item: {str(e)}")
        }
