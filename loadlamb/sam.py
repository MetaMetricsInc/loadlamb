import sammy as sm

f = sm.Function(name='loadlambpush',
                FunctionName='loadlamb-push',
                CodeUri=sm.S3URI(
                    Bucket=sm.Ref(Ref='Bucket'),
                    Key=sm.Ref(Ref='CodeZipKey')),
                Handler='loadlamb.lambdas.kinesis_push_handler',
                Runtime='python3.6'
                )

f2 = sm.Function(
    name='loadlambpull',
    FunctionName='loadlamb-pull',
    CodeUri=sm.S3URI(
        Bucket=sm.Ref(Ref='Bucket'),
        Key=sm.Ref(Ref='CodeZipKey')
    ),
    Handler='loadlamb.lambdas.kinesis_pull_handler',
    Runtime='python3.6'
)

db = sm.SimpleTable(
    name='loadlamb',
    PrimaryKey={'Name':'_id','Type':'String'}
)

s = sm.SAM(render_type='yaml')
s.add_parameter(sm.Parameter(name='Bucket', Type='String'))

s.add_parameter(sm.Parameter(name='CodeZipKey', Type='String'))
s.add_resource(f)
s.add_resource(f2)
s.add_resource(db)
