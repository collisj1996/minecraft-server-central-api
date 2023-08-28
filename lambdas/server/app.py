import json
from core.services import home_service

def lambda_handler(event, context):

    home_service.ping()

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": home_service.ping(),
        }),
    }
