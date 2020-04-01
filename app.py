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
            if action == 'get':
                return [bucket['Name'] for bucket in aws.listAllS3Buckets()]
            return 'Action not found!'
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
api.add_resource(S3RestAPI, '/s3/<string:action>/', methods=['GET'])

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port='3000')

# class RESTapp(Resource):
#     @staticmethod
#     def get(path=''):  # <-- You should provide the default here not in api.add_resource()!
#         return 'You want path: \'%s\'' % path  # do get something
# api.add_resource(RESTapp, '/', '/<path:path>')
