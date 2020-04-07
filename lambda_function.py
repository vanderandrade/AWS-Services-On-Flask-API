import boto3
import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

sqs_client = boto3.client('sqs')

QUEUE_NAME = 'final_queue'
def get_queue_url():
    return sqs_client.get_queue_url(QueueName=QUEUE_NAME).get('QueueUrl')

def lambda_handler(event, context):
    try:
        logger.info(event)
        
        for record in event['Records']:
            data = record['body']
            queue_url = get_queue_url()
            response = sqs_client.send_message(QueueUrl=queue_url, MessageBody=str(data))
            logger.info(data)
        
        return {
            'statusCode': 200,
            'body': json.dumps('Success!')
        }
    except Exception as e:
        logger.info('Failure')
        raise Exception("Could not record info! %s" % e)