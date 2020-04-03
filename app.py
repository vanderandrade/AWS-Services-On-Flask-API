import json
from flask import Flask, jsonify, request
from flask_restful import Resource, Api
import aws

app = Flask(__name__)
api = Api(app)

class S3RestAPI(Resource):
    def get(self, action: str):
        try:
            print(request.url)
            if action == 'getAllBuckets':
                return [bucket['Name'] for bucket in aws.listAllS3Buckets()]
            return 'Action not found!'
        except:
            return 'Not ok'
        
    def post(self, action: str):
        try:
            if action == 'createBucket':
                bucketName = request.form['bucket_name']
                region = request.form ['region'] if 'region' in request.form else None
                aws.createS3Bucket(bucketName, region)
            
            return 'Ok'
        except:
            return 'Not ok'

class EC2RestAPI(Resource):
    def post(self, action: str, payload=None):
        try:
            aws.turnEC2Instances(aws.Action[action], [request.form['instance_id']])
            return 'Ok'
        except:
            return {'Error':'Not ok'}

api.add_resource(EC2RestAPI, '/ec2/<string:action>/', methods=['POST']) # methods=['GET', 'POST']
api.add_resource(S3RestAPI, '/s3/<string:action>/', methods=['GET', 'POST'])

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port='3000')