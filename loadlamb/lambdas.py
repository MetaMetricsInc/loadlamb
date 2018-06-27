import json

import boto3

from envs import env

from loadlamb.load import LoadLamb

sns = boto3.client('sns', region_name='us-east-1')


def push_handler(event,context):
    print('User Number',event['user_num'])
    for i in range(event['user_num']):
        sns.publish(
            TopicArn=env('SNS_TOPIC_ARN'),
            Message=json.dumps(event)
        )


def pull_handler(event,context):
    msg = json.loads(event['Records'][0]['Sns']['Message'])
    print(msg)
    responses = LoadLamb(msg).run()
    print('RESPONSES',responses)