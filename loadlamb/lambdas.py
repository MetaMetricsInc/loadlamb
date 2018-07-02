import json

import boto3

from loadlamb.load import LoadLamb
from loadlamb.utils import grouper

sqs = boto3.resource('sqs')


def push_handler(event,context):
    print('User Number',event['user_num'])
    q = sqs.get_queue_by_name(QueueName='loadlamb')
    g = grouper(event['user_batch_size'],event['user_num'])
    for s in g:
        b = [{'Id':str(i),'MessageBody':json.dumps(event)} for i in range(s)]

        r = q.send_messages(Entries=b)



def pull_handler(event,context):
    msg = json.loads(event['Records'][0]['body'])
    print(msg)
    responses = LoadLamb(msg).run()
    print('RESPONSES',responses)