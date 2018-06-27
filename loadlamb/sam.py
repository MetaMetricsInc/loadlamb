import sammy as sm


sns = sm.SNS(name='SNSTopic')

sns_event = sm.SNSEvent(
    name='loadlamb',
    Topic=sm.Ref(Ref='SNSTopic')
)

env_vars = sm.Environment(Variables={
    'SNS_TOPIC_ARN':sm.Ref(Ref='SNSTopic')
})

f = sm.Function(name='loadlambpush',
                FunctionName='loadlamb-push',
                CodeUri=sm.S3URI(
                    Bucket=sm.Ref(Ref='CodeBucket'),
                    Key=sm.Ref(Ref='CodeZipKey')),
                Handler='loadlamb.lambdas.push_handler',
                Environment=env_vars,
                Runtime='python3.6'
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
    Environment=env_vars,
    Events=[sns_event]
)

db = sm.SimpleTable(
    name='loadlamb',
    PrimaryKey={'Name':'_id','Type':'String'}
)

s = sm.SAM(render_type='yaml')
s.add_parameter(sm.Parameter(name='CodeBucket', Type='String'))
s.add_parameter(sm.Parameter(name='CodeZipKey', Type='String'))
s.add_resource(sns)
s.add_resource(f)
s.add_resource(f2)
s.add_resource(db)
