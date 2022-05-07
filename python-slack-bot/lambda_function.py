import boto3
import json
import logging
import os

from base64 import b64decode
from urllib.parse import parse_qs
from commands.weather import Weather
from config import Config

config = Config()

kms = boto3.client("kms")
expected_token = kms.decrypt(
    CiphertextBlob=b64decode(config.ENCRYPTED_EXPECTED_TOKEN),
    EncryptionContext={"LambdaFunctionName": os.environ["AWS_LAMBDA_FUNCTION_NAME"]},
)["Plaintext"].decode("utf-8")

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def respond(err, res=None):
    if err:
        return {
            "statusCode": "400",
            "body": err.message,
            "headers": {
                "Content-Type": "application/json",
            },
        }
    else:
        return {
            "statusCode": "200",
            "body": "",
            "headers": {
                "Content-Type": "application/json",
            },
        }


def lambda_handler(event, context):
    logger.info(context)
    params = parse_qs(event["body"])
    print(params)
    token = params["token"][0]
    if token != expected_token:
        logger.error("Request token (%s) does not match expected", token)
        return respond(Exception("Invalid request token"))

    weather = Weather(params)
    res = weather.process()
    logger.info(res)
    return respond(None)
