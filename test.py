from requests import post, get

host='0.0.0.0'
port='3000'
_ec2_machine_id = ''

_response = get(f'http://{host}:{port}/s3/getAllBuckets/').json()
print(f'S3 Buckets: {_response}')

_response2 = post(f'http://{host}:{port}/ec2/stop/', data={'instance_id': _ec2_machine_id}).json()
print(f'Turn off EC2 machine: {_response2}')

bucket_name = ''
_response3 = post(f'http://{host}:{port}/s3/createBucket/', data={'bucket_name': bucket_name}).json()
print(f'Creating bucket: {_response3}')

filePath = ''
_response4 = post(f'http://{host}:{port}/s3/addFile/', data={'bucket_name': bucket_name, 'file_path' : filePath}).json()
print(f'Adding file on bucket: {_response4}')