import datetime
import json
import time
import logging
from multiprocessing import Pipe, Process

import boto3
from slugify import slugify
from valley.exceptions import ValidationException

from loadlamb.chalicelib.contrib.db.models import Project, Run,LoadTestResponse
from loadlamb.chalicelib.load import LoadLamb
from loadlamb.chalicelib.utils import grouper

sqs = boto3.resource('sqs')


def create_run_record(event):
    project_slug = slugify(event['name'])
    run_slug = slugify('{}-{}'.format(event['name'],datetime.datetime.now()))
    event['run_slug'] = run_slug
    event['project_slug'] = project_slug
    url = event['url']
    user_num = event['user_num']
    
    try:
        p = Project(project_slug=project_slug)
        p.save()
    except ValidationException as ve:
        # If the ValidationException is raised, it is assumed that the project
        # already exists as a "Project" entry. Ignore and carry on.
        pass
    
    r = Run(project_slug=project_slug,run_slug=run_slug,url=url,user_num=user_num)
    r.save()
    return event


def push_handler(event,context):
    try:
        delay = event.get('delay')
        if delay:
            time.sleep(int(delay))
        event = create_run_record(event)
        q = sqs.get_queue_by_name(QueueName='loadlamb')
        g = grouper(event['user_batch_size'],event['user_num'])
        for s in g:
            b = [{'Id':str(i),'MessageBody':json.dumps(event)} for i in range(s)]
            r = q.send_messages(Entries=b)
    except Exception as e:
        # This is a capital crime punishable by death of a project but...
        # I think it is necessary so we don't have runaway lambdas because
        # if we have an error here the message will never come off of the queue
        logging.error(e)


class RunLoadLamb(object):
    """Finds total volume size for all EC2 instances"""

    def __init__(self, event):
        self.msgs = [json.loads(i['body']) for i in event['Records']]

    def run_loadlamb(self, msg, conn):
        try:
            responses = LoadLamb(msg).run()
            LoadTestResponse.bulk_save(responses)
        except Exception as e:
            logging.error(e)
        conn.close()

    def process_msgs(self):
        """
        Lists all EC2 instances in the default region
        and sums result of instance_volumes
        """
        

        # create a list to keep all processes
        processes = []

        # create a list to keep connections
        parent_connections = []

        # create a process per instance
        for msg in self.msgs:
            # create a pipe for communication
            parent_conn, child_conn = Pipe()
            parent_connections.append(parent_conn)

            # create the process, pass instance and connection
            process = Process(target=self.run_loadlamb, args=(msg, child_conn,))
            processes.append(process)

        # start all processes
        for process in processes:
            process.start()

        # make sure that all processes have finished
        for process in processes:
            process.join()

        return "Ok"

def pull_handler(event,context):
    try:
        rl = RunLoadLamb(event)
        return rl.process_msgs()
    except Exception as e:
        # This is a capital crime punishable by death of a project but...
        # I think it is necessary so we don't have runaway lambdas because
        # if we have an error here the message will never come off of the queue
        logging.error(e)
