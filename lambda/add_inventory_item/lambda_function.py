import json
import boto3
import os
import uuid  # using uuid4


# Set up DynamoDB resource and table
dynamodb = boto3.resource('dynamodb')
TABLE_NAME = os.getenv('TABLE_NAME', 'inventory')  # default to 'inventory'
table = dynamodb.Table(TABLE_NAME)

def lambda_handler(event, context):
    # 1. Parse incoming JSON body
    try:
        body = event.get('body', '{}')  # API Gateway sends body as a string
        data = json.loads(body)
    except (TypeError, json.JSONDecodeError):
        return {
            "statusCode": 400,
            "body": json.dumps("Bad request. Please provide valid JSON in the body.")
        }

    # 2. Validate required fields
    required_fields = [
        "item_name",
        "item_description",
        "qty_on_hand",
        "item_price",
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
        "ItemId": item_id,                          # PK (string, UUID4)
        "LocationId": int(data["location_id"]),     # SK (integer)
        "ItemName": data["item_name"],
        "ItemDescription": data["item_description"],
        "QtyOnHand": int(data["qty_on_hand"]),
        "ItemPrice": float(data["item_price"])
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
