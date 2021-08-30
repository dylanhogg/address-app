import os
import argparse
import json
from datetime import datetime
from addressnet.predict import predict_one


def lambda_handler(event, context):
    """Lambda function handler
    Parameters
    ----------
    event: dict, required
        API Gateway Lambda Proxy Input Format
        Event doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format
    context: object, required
        Lambda Context runtime methods and attributes
        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html
    Returns
    ------
    API Gateway Lambda Proxy Output Format: dict
        Return doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
    """
    start = datetime.now()

    print(f'INFO: event: [{event}]')

    if not "body" in event:
        raise Exception("body key not found in event")

    data = event["body"]
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except ValueError as e:
            raise Exception(f"body key is not valid json")

    if data is None:
        raise Exception("event body is empty")

    # TODO: test dict type

    if not "address" in data:
        raise Exception("address key not found in event body")

    address = data["address"]

    max_address_length = 150
    if len(address) > max_address_length:
        raise Exception(f"address length must be less than {max_address_length} chars")

    model_dir = "/opt/ml/model/pretrained"
    predict_result = predict_one(address, model_dir)

    print(f'INFO: address: [{address}] -> predict_result: {predict_result}')

    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "address": address,
                "result": predict_result,
                "time": str(datetime.now() - start),
                "version": "0.1.5"
            }
        ),
        "headers": {
            "Access-Control-Allow-Origin": "*",
        },
        "isBase64Encoded": False
    }
