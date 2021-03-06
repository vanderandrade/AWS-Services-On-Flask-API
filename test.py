from requests import post, get
import json

host='0.0.0.0'
port='3000'

_ec2_instance_id = ''

bucket_name = ''
file = ''

def test_getAllBuckets():
    response = get(f'http://{host}:{port}/s3/getAllBuckets/').json()
    print(f'S3 Buckets: {response}')

def test_turnOnEC2Instance(instanceId):
    response = post(f'http://{host}:{port}/ec2/start/', data={'instance_id': instanceId}).json()
    print(f'Turn on EC2 instance: {response}')

def test_turnOffEC2Instance(instanceId):
    response = post(f'http://{host}:{port}/ec2/stop/', data={'instance_id': instanceId}).json()
    print(f'Turn off EC2 instance: {response}')

def test_createBucket(bucketName):
    response = post(f'http://{host}:{port}/s3/createBucket/', data={'bucket_name': bucketName}).json()
    print(f'Creating bucket: {response}')

def test_addFileOnBucket(bucketName, filePath):
    response = post(f'http://{host}:{port}/s3/addFile/', data={'bucket_name': bucketName, 'file_path' : filePath}).json()
    print(f'Adding file on bucket: {response}')

def test_safeDeleteBucket(bucketName):
    response = post(f'http://{host}:{port}/s3/deleteBucket/', data={'bucket_name': bucketName}).json()
    print(f'Deleting bucket: {response}')

def test_deleteFileOnBucket(bucketName, fileName):
    response = post(f'http://{host}:{port}/s3/deleteFile/', data={'bucket_name': bucketName, 'file_name' : fileName}).json()
    print(f'removing file on bucket: {response}')

def test_createSQSQueue(queueName, isFifo='false'):
    response = post(f'http://{host}:{port}/sqs/create/', data={'name': queueName, 'fifo' : isFifo}).json()
    print(f'creating queue: {response}')

def test_sendMessageToSQSQueue(queueName, message):
    response = post(f'http://{host}:{port}/sqs/sendMessage/', data={'queue_name': queueName, 'message' : message}).json()
    print(f'sending message: {response}')

#test_createBucket(bucket_name)
#test_safeDeleteBucket(bucket_name)

#test_createSQSQueue('test-queue', 'false')
test_sendMessageToSQSQueue('initial-queue', 'second message')