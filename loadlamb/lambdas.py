import datetime
import json
import time

import boto3
from slugify import slugify

from loadlamb.contrib.db.models import Run
from loadlamb.load import LoadLamb
from loadlamb.utils import grouper

sqs = boto3.resource('sqs')


def create_run_record(event):
    project_slug = slugify(event['name'])
    run_slug = slugify('{}-{}'.format(event['name'],datetime.datetime.now()))
    event['run_slug'] = run_slug
    event['project_slug'] = project_slug
    r = Run(project_slug=project_slug,run_slug=run_slug)
    r.save()
    return event


def push_handler(event,context):
    delay = event.get('delay')
    if delay:
        time.sleep(int(delay))
    print('User Number',event['user_num'])
    event = create_run_record(event)
    q = sqs.get_queue_by_name(QueueName='loadlamb')
    g = grouper(event['user_batch_size'],event['user_num'])
    for s in g:
        b = [{'Id':str(i),'MessageBody':json.dumps(event)} for i in range(s)]
        r = q.send_messages(Entries=b)


def pull_handler(event,context):
    msg = json.loads(event['Records'][0]['body'])
    print(msg)
    responses = LoadLamb(msg).run()
    for i in responses:
        i.save()
