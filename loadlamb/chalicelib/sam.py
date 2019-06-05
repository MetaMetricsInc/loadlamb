import datetime

import sammy as sm


env = sm.Environment(Variables={
    'DYNAMODB_TABLE': 'loadlambddb',
    'DEPLOYMENT_DATE': str(datetime.datetime.now())
})

role = sm.Role(
    name='loadlambpolicy',
    AssumeRolePolicyDocument={
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Principal": {
                "Service": ["lambda.amazonaws.com"]
            },
            "Action": ["sts:AssumeRole"]
        }]
    },
    ManagedPolicyArns=['arn:aws:iam::aws:policy/AmazonSQSFullAccess',
                       'arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess',
                       'arn:aws:iam::aws:policy/CloudWatchLogsFullAccess'],
    RoleName='loadlamb'
)

f = sm.Function(name='loadlambpush',
                FunctionName='loadlamb-run',
                CodeUri=sm.S3URI(
                    Bucket=sm.Ref(Ref='CodeBucket'),
                    Key=sm.Ref(Ref='CodeZipKey')),
                Handler='loadlamb.chalicelib.lambdas.run_handler',
                Runtime='python3.6',
                Timeout=900,
                MemorySize=3008,
                Role=sm.Sub(Sub='arn:aws:iam::${AWS::AccountId}:role/loadlamb'),
                Environment=env
                )

s = sm.SAM(render_type='yaml')
s.add_parameter(sm.Parameter(name='CodeBucket', Type='String'))
s.add_parameter(sm.Parameter(name='CodeZipKey', Type='String'))

s.add_resource(f)

r = sm.CFT(render_type='yaml')

r.add_resource(role)

bucket = sm.S3(name='bucket')
output = sm.Output(name='bucket', Description='S3 Topic Details', Value=sm.Ref(Ref='bucket'))
s3t = sm.CFT(render_type='yaml')
s3t.add_resource(bucket)
s3t.add_output(output)
