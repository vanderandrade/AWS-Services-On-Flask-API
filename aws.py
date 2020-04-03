import enum
import logging
import boto3
import botocore.exceptions
import hmac
import hashlib
import base64
import json

class Action(enum.Enum):
   stop = 0
   start = 1

def getAWSSession(profileName):
    try:
        return boto3.Session(profile_name=profileName)
    except botocore.exceptions.ClientError as e:
        logging.error(e)
        return None

def getAWSClient(service, profileName):
    try:
        session = getAWSSession(profileName)
        return session.client(service)
    except botocore.exceptions.ClientError as e:
        logging.error(e)
        return None
def getS3Client(profileName='s3_fullaccess'):
    return getAWSClient('s3', profileName)
def getEC2Client(profileName='ec2_fullaccess'):
    return getAWSClient('ec2', profileName)
def getCognitoIDClient(profileName='cognito_access'):
    return getAWSClient('cognito-identity', profileName)
def getCognitoIDPClient(profileName='cognito_access'):
    return getAWSClient('cognito-idp', profileName)

def getAWSResource(service, profileName):
    try:
        session = getAWSSession(profileName)
        return session.resource(service)
    except botocore.exceptions.ClientError as e:
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

def _createResponse(success: bool, error: bool, message, data) -> dict:
    return {"error": error, "success": success, "data": data, "message": message}
def _getSecretHash(username):
    msg = username + CLIENT_ID
    dig = hmac.new(str(CLIENT_SECRET).encode('utf-8'), 
        msg = str(msg).encode('utf-8'),
        digestmod=hashlib.sha256).digest()
    d2 = base64.b64encode(dig).decode()    
    return d2

## S3 functions ##
def createS3Bucket(bucketName, region=None):
    try:
        if region is None:
            s3_client = getS3Client()
            bucket_response = s3_client.create_bucket(Bucket=bucketName)
        else:
            s3_client = boto3.client('s3', region_name=region)
            location = {'LocationConstraint': region}
            bucket_response = s3_client.create_bucket(Bucket=bucketName, CreateBucketConfiguration=location)
        return bucket_response
    except botocore.exceptions.ClientError as e:
        logging.error(e)
        return None
def deleteSafeS3Bucket(bucketName):
    try:
        s3Client = getS3Client()
        response = s3Client.delete_bucket(Bucket=bucketName)
        return response
    except Exception as e:
        logging.error(e)
        return 'Error: Bucket not deleted'
def addFileToS3Bucket(bucketName, fileName):
    s3Resource = getS3Resource()
    s3Resource.Object(bucketName, fileName).upload_file(Filename=fileName)
def removeFileOnS3Bucket(bucketName, fileName):
    s3Client = getS3Client()
    response = s3Client.delete_object(
        Bucket=bucketName,
        Key=fileName
    )
    return response
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
    except botocore.exceptions.ClientError as e:
        print(e)
## ## ## ## ## ##

## Cognito functions ##
def initiateAuth(cognitoClient, username, password):
    secretHash = _getSecretHash(username)
    try:
        resp = cognitoClient.admin_initiate_auth(
                    UserPoolId=USER_POOL_ID,
                    ClientId=CLIENT_ID,
                    AuthFlow='ADMIN_NO_SRP_AUTH',
                    AuthParameters={
                        'USERNAME': username,
                        'SECRET_HASH': secretHash,
                        'PASSWORD': password,
                    },
                    ClientMetadata={
                        'username': username,
                        'password': password,              })
    except cognitoClient.exceptions.NotAuthorizedException:
        return None, "The username or password is incorrect"
    except cognitoClient.exceptions.UserNotConfirmedException:
        return None, "User is not confirmed"
    except Exception as e:
        return None, e.__str__()
    return resp, None
def sendChallengeResponseNewPasswordRequired(session, username, newPassword):
    client = getCognitoIDPClient()

    return client.respond_to_auth_challenge(
        ClientId=CLIENT_ID,
        ChallengeName='NEW_PASSWORD_REQUIRED',
        Session=session,
        ChallengeResponses={
            'NEW_PASSWORD': newPassword,
            'USERNAME': username,
            'SECRET_HASH': _getSecretHash(username)
        },
    )
def authenticateUserOnCognitoIdentityProvider(username, password):
    client = getCognitoIDPClient()

    resp, msg = initiateAuth(client, username, password)
    if msg != None:
        return _createResponse(False, True, msg, None)
    if resp.get("AuthenticationResult"):
        return _createResponse(
                    True,
                    False,
                    "success", 
                    {   "id_token": resp["AuthenticationResult"]["IdToken"],
                        "refresh_token": resp["AuthenticationResult"]["RefreshToken"],
                        "access_token": resp["AuthenticationResult"]["AccessToken"],
                        "expires_in": resp["AuthenticationResult"]["ExpiresIn"],
                        "token_type": resp["AuthenticationResult"]["TokenType"] })
    else:
        if resp['ChallengeName']:
            return _createResponse(False, True, resp['ChallengeName'], resp)
        return _createResponse(False, True, msg, resp)
## ## ## ## ## ## ## ##
def listCognitoIdentities(identityPoolId, maxResults=20):
    return getCognitoIDClient().list_identities(IdentityPoolId=identityPoolId, MaxResults=maxResults)
## ## ## ## ## ## ## ##

with open('info_cognito.json') as jsonFile:
    data = json.load(jsonFile)

    USER_POOL_ID = data['user_pool_id']
    CLIENT_ID = data['client_id']
    CLIENT_SECRET = data['client_secret']