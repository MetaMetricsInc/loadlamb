import sammy as sm



sqs = sm.SQS(name='SQSQueue',QueueName='loadlamb')

sqs_event = sm.SQSEvent(
    name='loadlambsqs',
    Queue=sm.Sub(Sub='arn:aws:sqs:${AWS::Region}:${AWS::AccountId}:loadlamb'),
    BatchSize=1
)

db = sm.SimpleTable(
    name='loadlambddb',
    PrimaryKey={'Name':'_id','Type':'String'}
)

env = sm.Environment(Variables={
    'DYNAMODB_TABLE':sm.Ref(Ref='loadlambddb')
})

role = sm.Role(
    name='loadlambpolicy',
    AssumeRolePolicyDocument={
               "Version" : "2012-10-17",
               "Statement": [ {
                  "Effect": "Allow",
                  "Principal": {
                     "Service": [ "lambda.amazonaws.com" ]
                  },
                  "Action": [ "sts:AssumeRole" ]
               } ]
            },
    ManagedPolicyArns=['arn:aws:iam::aws:policy/AmazonSQSFullAccess',
                       'arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess',
                       'arn:aws: iam::aws:policy/CloudWatchLogsFullAccess'],
    RoleName='loadlamb'
)

f = sm.Function(name='loadlambpush',
                FunctionName='loadlamb-push',
                CodeUri=sm.S3URI(
                    Bucket=sm.Ref(Ref='CodeBucket'),
                    Key=sm.Ref(Ref='CodeZipKey')),
                Handler='loadlamb.lambdas.push_handler',
                Runtime='python3.6',
                Role=sm.Sub(Sub='arn:aws:iam::${AWS::AccountId}:role/loadlamb'),
                Environment=env
                )

f2 = sm.Function(
    name='loadlambpull',
    FunctionName='loadlamb-pull',
    CodeUri=sm.S3URI(
        Bucket=sm.Ref(Ref='CodeBucket'),
        Key=sm.Ref(Ref='CodeZipKey')
    ),
    Handler='loadlamb.lambdas.pull_handler',
    Runtime='python3.6',
    Events=[sqs_event],
    Environment=env
)



s = sm.SAM(render_type='yaml')
s.add_parameter(sm.Parameter(name='CodeBucket', Type='String'))
s.add_parameter(sm.Parameter(name='CodeZipKey', Type='String'))
s.add_resource(sqs)
s.add_resource(f)
s.add_resource(f2)
s.add_resource(db)
s.add_resource(role)
