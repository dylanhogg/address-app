import json
import uuid
import boto3
from typing import Dict
from datetime import datetime
from dataclasses import dataclass
from addressnet.predict import predict_one

runtime_start = datetime.now()
app_version = "0.1.15"
model_dir = "/opt/ml/model/pretrained"
dynamodb = boto3.resource('dynamodb')


@dataclass
class ApiResult:
    response_body: str = ""
    address: str = ""
    ip_address: str = ""
    user_agent: str = ""


class SafeDict(dict):
    def __missing__(self, key):
        value = self[key] = type(self)()
        return value


def predict_address(address) -> Dict[str, str]:
    return predict_one(address, model_dir)


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

    predict_result = predict_address(address)
    response_body = json.dumps(
        {
            "address": address,
            "result": predict_result,
            "handler_time": str(datetime.now() - handler_start),
            "runtime_time": str(datetime.now() - runtime_start),
            "model_dir": model_dir,
            "version": app_version
        })

    ip_address = event["requestContext"]["identity"]["sourceIp"]
    user_agent = event["requestContext"]["identity"]["userAgent"]
    return ApiResult(response_body, address, ip_address, user_agent)


def save_response(request_id, success, api_result, event, response) -> bool:
    try:
        table = dynamodb.Table("address-api-infocruncher-com-usage")
        table.put_item(
            Item={
                "requestId": request_id,
                "datetime": str(datetime.now()),
                "success": success,
                "address": api_result.address,
                "ip_address": api_result.ip_address,
                "user_agent": api_result.user_agent,
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
    allow_origin = "*"   # TODO: lockdown Access-Control-Allow-Origin value below?
    api_result = ApiResult()

    print(f'INFO: source event: {event}')
    print(f'INFO: source context: {context}')

    try:
        event = SafeDict(event)
        api_result = handle_api_event(event, handler_start)
        success_response = {
            "statusCode": 200,
            "body": api_result.response_body,
            "headers": {
                "Access-Control-Allow-Origin": allow_origin,
            },
            "isBase64Encoded": False
        }
        if not is_scheduled_event(event):
            print(f'INFO: api_result: [{api_result}]')
            save_response(request_id, True, api_result, event, success_response)
        return success_response

    except Exception as ex:
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
        if not is_scheduled_event(event):
            print("ERROR: " + str(ex))
            print(f'INFO: error_response: [{error_response}]')
            save_response(request_id, False, api_result, event, error_response)
        return error_response
