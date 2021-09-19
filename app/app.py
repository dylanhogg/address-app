import json
import uuid
import boto3
from typing import Dict
from datetime import datetime
from library.classes import ApiResult, SafeDict
from addressnet.predict import predict_one

runtime_start = datetime.now()
app_version = "1.0.0"
model_dir = "/opt/ml/model/pretrained"
allow_origin = "*"   # TODO: lockdown Access-Control-Allow-Origin value below?
dynamodb_table = "AddressPredictionInferenceFunctionUsage"

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(dynamodb_table)


def handle_api_event(event, handler_start) -> ApiResult:
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

    if "address" not in data:
        raise Exception("address key not found in event body")

    # TODO: handle multiple address input
    address = data["address"].strip()

    if len(address) == 0:
        raise Exception("Address is empty")

    # For debugging
    if address == "SimulateError":
        raise Exception("Simulate error")

    max_address_length = 150
    if len(address) > max_address_length:
        raise Exception(f"address length must be less than {max_address_length} chars")

    predict_result = predict_one(address, model_dir)
    handler_time = str(datetime.now() - handler_start)
    runtime_time = str(datetime.now() - runtime_start)
    response_body = json.dumps(
        {
            "address": address,
            "result": predict_result,
            "handler_time": handler_time,
            "runtime_time": runtime_time,
            "model_dir": model_dir,
            "version": app_version
        })

    ip_address = event["requestContext"]["identity"]["sourceIp"]
    user_agent = event["requestContext"]["identity"]["userAgent"]
    return ApiResult(response_body, address, ip_address, user_agent, handler_time, runtime_time)


def save_response(request_id, success, api_result, event, response) -> bool:
    try:
        # table = dynamodb.Table(dynamodb_table)
        table.put_item(
            Item={
                "requestId": request_id,
                "datetime": str(datetime.now()),
                "success": success,
                "address": api_result.address,
                "ip_address": api_result.ip_address,
                "user_agent": api_result.user_agent,
                "handler_time": api_result.handler_time,
                "runtime_time": api_result.runtime_time,
                "response": response,
                "event": event,
                "app_version": app_version
            }
        )
        return True
    except Exception as ex:
        print(f"ERROR: dynamodb log exception: {ex}")
        return False


def is_scheduled_event(event) -> bool:
    return "detail-type" in event and event["detail-type"] == "Scheduled Event"


def lambda_handler(event, context) -> Dict[str, str]:
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

    request_id = uuid.uuid4().hex
    handler_start = datetime.now()
    api_result = None

    print(f'INFO: source event: {event}')
    print(f'INFO: source context: {context}')

    try:
        event = SafeDict(event)

        if is_scheduled_event(event):
            scheduled_response = {
                "statusCode": 200,
                "body": json.dumps(
                    {
                        "scheduled_event": "True",
                        "handler_time": str(datetime.now() - handler_start),
                        "runtime_time": str(datetime.now() - runtime_start),
                        "model_dir": model_dir,
                        "version": app_version
                    }
                ),
                "isBase64Encoded": False
            }
            print(f'INFO: scheduled_event called')
            return scheduled_response

        api_result = handle_api_event(event, handler_start)
        success_response = {
            "statusCode": 200,
            "body": api_result.response_body,
            "headers": {
                "Access-Control-Allow-Origin": allow_origin,
            },
            "isBase64Encoded": False
        }

        print(f'INFO: api_result: [{api_result}]')
        save_response(request_id, True, api_result, event, success_response)
        return success_response

    except Exception as ex:
        print("ERROR: " + str(ex))
        error_response = {
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
        print(f'INFO: error_response: [{error_response}]')

        if api_result is None:
            api_result = ApiResult(response_body=error_response,
                                   handler_time=str(datetime.now() - handler_start),
                                   runtime_time=str(datetime.now() - runtime_start))
        save_response(request_id, False, api_result, event, error_response)
        return error_response
