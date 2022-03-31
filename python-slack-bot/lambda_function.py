import boto3
import json
import logging
import os

from base64 import b64decode
from urllib.parse import parse_qs
from commands.weather import Weather
from config import Config

config = Config()

kms = boto3.client('kms')
expected_token = kms.decrypt(
    CiphertextBlob=b64decode(config.ENCRYPTED_EXPECTED_TOKEN),
    EncryptionContext={'LambdaFunctionName': os.environ['AWS_LAMBDA_FUNCTION_NAME']}
)['Plaintext'].decode('utf-8')

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def respond(err, res=None):
    return {
        'statusCode': '400' if err else '200',
        'body': err.message if err else json.dumps(res).encode('utf8'),
        'headers': {
            'Content-Type': 'application/json',
        },
    }

def lambda_handler(event, context):
    params = parse_qs(event['body'])
    token = params['token'][0]
    if token != expected_token:
        logger.error("Request token (%s) does not match expected", token)
        return respond(Exception('Invalid request token'))
    
    weather = Weather(params)
    res = weather.process()
    logger.info(res)
    return respond(None, "Processing Complete")
