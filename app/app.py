import json
from datetime import datetime
from addressnet.predict import predict_one

runtime_start = datetime.now()
app_version = "0.1.10"
model_dir = "/opt/ml/model/pretrained"


def predict_address(address):
    result = predict_one(address, model_dir)

    print(f'INFO: predict_address: [{address}] -> result: {result}')

    return result


def handle_api_event(event, handler_start):
    if "body" not in event:
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

    if "address" not in data:
        raise Exception("address key not found in event body")

    address = data["address"]

    # TEMP:
    if address == "SimulateError":
        raise Exception("Simulated error")

    max_address_length = 150
    if len(address) > max_address_length:
        raise Exception(f"address length must be less than {max_address_length} chars")

    predict_result = predict_address(address)

    api_body = json.dumps(
        {
            "address": address,
            "result": predict_result,
            "handler_time": str(datetime.now() - handler_start),
            "runtime_time": str(datetime.now() - runtime_start),
            "model_dir": model_dir,
            "version": app_version
        })

    print(f'INFO: api_body: [{api_body}]')
    return api_body


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

    handler_start = datetime.now()
    allow_origin = "*"   # TODO: lockdown Access-Control-Allow-Origin value below?

    print(f'INFO: source event: {event}')
    print(f'INFO: source context: {context}')

    try:
        # TODO: work out if a warmer event and handle accordingly

        response_body = handle_api_event(event, handler_start)

        success_api_result = {
            "statusCode": 200,
            "body": response_body,
            "headers": {
                "Access-Control-Allow-Origin": allow_origin,
            },
            "isBase64Encoded": False
        }
        print(f'INFO: success_api_result: [{success_api_result}]')
        return success_api_result

    except Exception as ex:
        # TODO: remove error detail below
        print("ERROR: " + str(ex))
        error_api_result = {
            "statusCode": 500,
            "body": json.dumps(
                {
                    "error": str(ex),
                    "handler_time": str(datetime.now() - handler_start),
                    "runtime_time": str(datetime.now() - runtime_start),
                    "model_dir": model_dir,
                    "version": app_version
                }
            ),
            "headers": {
                "Access-Control-Allow-Origin": allow_origin,
            },
            "isBase64Encoded": False
        }
        print(f'INFO: error_api_result: [{error_api_result}]')
        return error_api_result
