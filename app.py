import json
from flask import Flask, jsonify, request
from flask_restful import Resource, Api
import aws

app = Flask(__name__)
api = Api(app)

def _createResponse(success: bool, error: bool, message, data) -> dict:
    return {"success": success, "error": error, "data": data, "message": message}
def _createGenericErrorResponse() -> dict:
    return _createResponse(False, True, 'Not ok', None)

class SQSRestAPI(Resource):
    def post(self, action):
        try:
            if action == 'create':
                response = aws.createSQSQueue(request.form['name'], request.form['fifo'])
                return _createResponse(True, False, 'Ok', response['QueueUrl'])
            elif action == 'sendMessage':
                response = aws.sendMessageToSQSQueue(request.form['queue_name'], request.form['message'])
                return _createResponse(True, False, 'Ok', response)
            return _createResponse(True, False, 'Ok', None)
        except Exception as e:
            print(e)
            return _createGenericErrorResponse()

class S3RestAPI(Resource):
    def get(self, action: str):
        try:
            print(request.url)
            if action == 'getAllBuckets':
                bucketsNames = [bucket['Name'] for bucket in aws.listAllS3Buckets()]
                return _createResponse(True, False, 'Success', bucketsNames)
            return _createResponse(False, True, 'Action not found!', None)
        except:
            return _createGenericErrorResponse()
        
    def post(self, action: str):
        try:
            if action == 'createBucket':
                bucketName = request.form['bucket_name']
                region = request.form['region'] if 'region' in request.form else None
                
                aws.createS3Bucket(bucketName, region)
            elif action == 'deleteBucket':
                bucketName = request.form['bucket_name']
                
                response = aws.deleteSafeS3Bucket(bucketName)

                print(response)
            elif action == 'addFile':
                bucketName = request.form['bucket_name']
                filePath = request.form['file_path']

                aws.addFileToS3Bucket(bucketName, filePath)
            elif action == 'deleteFile':
                bucketName = request.form['bucket_name']
                fileName = request.form['file_name']

                aws.removeFileOnS3Bucket(bucketName, fileName)

            return _createResponse(True, False, 'Ok', None)
        except:
            return _createGenericErrorResponse()

class EC2RestAPI(Resource):
    def post(self, action: str):
        try:
            aws.turnEC2Instances(aws.Action[action], [request.form['instance_id']])
            return _createResponse(True, False, 'Ok', None)
        except:
            return _createGenericErrorResponse()

api.add_resource(EC2RestAPI, '/ec2/<string:action>/', methods=['POST'])
api.add_resource(SQSRestAPI, '/sqs/<string:action>/', methods=['POST'])
api.add_resource(S3RestAPI, '/s3/<string:action>/', methods=['GET', 'POST'])

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port='3000')