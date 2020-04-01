from requests import post, get

host='0.0.0.0'
port='3000'
_ec2_machine_id = ''

_response = get(f'http://{host}:{port}/s3/get/').json()
print(f'S3 Buckets: {_response}')

_response2 = post(f'http://{host}:{port}/ec2/stop/', data={'instance_id': _ec2_machine_id}).json()
print(f'Turn off EC2 machine: {_response2}')