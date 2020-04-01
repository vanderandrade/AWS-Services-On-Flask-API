import enum
import logging
import boto3
from botocore.exceptions import ClientError

class Action(enum.Enum):
   stop = 0
   start = 1

def getAWSSession(profileName):
    try:
        return boto3.Session(profile_name=profileName)
    except ClientError as e:
        logging.error(e)
        return None

def getAWSClient(service, profileName):
    try:
        session = getAWSSession(profileName)
        return session.client(service)
    except ClientError as e:
        logging.error(e)
        return None
def getS3Client(profileName='s3_fullaccess'):
    return getAWSClient('s3', profileName)
def getEC2Client(profileName='ec2_fullaccess'):
    return getAWSClient('ec2', profileName)

def getAWSResource(service, profileName):
    try:
        session = getAWSSession(profileName)
        return session.resource(service)
    except ClientError as e:
        logging.error(e)
        return None
def getS3Resource(profileName='s3_fullaccess'):
    return getAWSResource('s3', profileName)
def getEC2Resource(profileName='ec2_fullaccess'):
    return getAWSResource('ec2', profileName)

_actionsEC2Monitoring = {
    Action.start: lambda ids: getEC2Client().monitor_instances(InstanceIds=ids),
    Action.stop: lambda ids: getEC2Client().unmonitor_instances(InstanceIds=ids)
    }
_actionsEC2Instances = {
    Action.start: lambda ids: getEC2Client().start_instances(InstanceIds=ids),
    Action.stop: lambda ids: getEC2Client().stop_instances(InstanceIds=ids)
    }

## S3 functions ##
def createS3Bucket(bucket_name, region=None):
    try:
        if region is None:
            s3_client = boto3.client('s3')
            bucket_response = s3_client.create_bucket(Bucket=bucket_name)
        else:
            s3_client = boto3.client('s3', region_name=region)
            location = {'LocationConstraint': region}
            bucket_response = s3_client.create_bucket(Bucket=bucket_name, CreateBucketConfiguration=location)
        return bucket_response
    except ClientError as e:
        logging.error(e)
        return None
def addFileToS3Bucket(bucketName, fileName):
    s3Resource = getS3Resource()
    s3Resource.Object(bucketName, fileName).upload_file(Filename=fileName)
def listAllS3Buckets():
    s3Client = getS3Client()
    response = s3Client.list_buckets()

    return response['Buckets']
## ## ## ## ## ##

## EC2 functions ##
def turnMonitoringInEC2Instances(action: Action, instanceIds: list):
    return _actionsEC2Monitoring[action](instanceIds)
def turnEC2Instances(action: Action, instanceIds: list):
    return _actionsEC2Instances[action](instanceIds)
def listAllEC2Reservations():
    ec2Response = getEC2Client().describe_instances()
    return ec2Response['Reservations']
def listEC2Instances(instancesId=[]):
    try:
        return list(getEC2Resource().instances.filter(InstanceIds=instancesId))
    except ClientError as e:
        print(e)
## ## ## ## ## ##