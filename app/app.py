import os
import argparse
import json
from addressnet.predict import predict_one
from loguru import logger


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

    # parser = argparse.ArgumentParser()
    # parser.add_argument("model_dir", help="Pretrained model directory")
    # parser.add_argument("address", help="Address string")
    # args = parser.parse_args()
    #
    # predict_result = predict_one(args.address, args.model_dir)
    # logger.info(f'Model file    : {args.model_dir}')
    # logger.info(f'Input address : {args.address}')
    # logger.info(f'Predict result: {predict_result}')

    # return {
    #     'statusCode': 200,
    #     'body': json.dumps(
    #         {
    #             "event": event
    #         }
    #     )
    # }

    version = "0.1.4"

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
    model_dir = "/opt/ml/model/pretrained"
    predict_result = predict_one(address, model_dir)

    logger.info(f'address: [{address}] -> predict_result: {predict_result}')

    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "address": address,
                "predict_result": predict_result,
                "version": version
            }
        ),
        "isBase64Encoded": False
    }
