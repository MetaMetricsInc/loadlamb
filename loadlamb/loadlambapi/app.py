import docb
import requests
from docb.loading import DocbHandler
from envs import env
from chalice import Chalice

app = Chalice(app_name='loadlambapi')


def get_db_kwargs():
    kwargs = {
        'dynamodb': {
            'connection': {
                'table': 'loadlambddb'
            },
            'documents': ['loadlamb.contrib.db.models.Run', 'loadlamb.contrib.db.models.LoadTestResponse'],
            'table_config': {
                'write_capacity': 100,
                'read_capacity': 100
            }
        },

    }
    if env('DYNAMODB_ENDPOINT_URL', None):

        kwargs['dynamodb']['config'] = {
            'endpoint_url': 'http://dynamodb:8000'
        }
        kwargs['dynamodb']['table_config'] = {
            'write_capacity': 100,
            'read_capacity': 100,
            'secondary_write_capacity': 100,
            'secondary_read_capacity': 100
        }
    return kwargs


docb_handler = DocbHandler(get_db_kwargs())


class Project(docb.Document):
    name = docb.CharProperty(required=True)
    project_slug = docb.SlugProperty(required=True, unique=True)
    repo_url = docb.CharProperty()
    url = docb.CharProperty()

    def __unicode__(self):
        return self.name

    class Meta:
        use_db = 'dynamodb'
        handler = docb_handler


class Run(docb.Document):
    run_slug = docb.SlugProperty(global_index=True, unique=True)
    project_slug = docb.SlugProperty(global_index=True)
    requests = docb.IntegerProperty(required=False)
    requests_per_second = docb.FloatProperty(required=False)
    elapsed_time = docb.FloatProperty(required=False)
    commit = docb.CharProperty(required=False)
    last_updated = docb.DateTimeProperty(auto_now=True)
    date_created = docb.DateTimeProperty(auto_now_add=True)
    user_batch_size = docb.IntegerProperty(required=False)
    user_batch_sleep = docb.IntegerProperty(required=False)
    status_500 = docb.IntegerProperty()
    status_200 = docb.IntegerProperty()
    status_400 = docb.IntegerProperty()
    error_msg = docb.CharProperty(required=False)
    completed = docb.BooleanProperty(default_value=False, required=False)

    def __unicode__(self):
        return self.run_slug

    class Meta:
        use_db = 'dynamodb'
        handler = docb_handler


class Group(docb.Document):
    run_slug = docb.SlugProperty(global_index=True)
    project_slug = docb.SlugProperty(global_index=True)
    group_no = docb.IntegerProperty(required=True)
    requests_per_second = docb.FloatProperty(required=False)
    elapsed_time = docb.FloatProperty(required=False)
    last_updated = docb.DateTimeProperty(auto_now=True)
    date_created = docb.DateTimeProperty(auto_now_add=True)
    status_500 = docb.IntegerProperty()
    status_200 = docb.IntegerProperty()
    status_400 = docb.IntegerProperty()
    error_msg = docb.CharProperty(required=False)
    completed = docb.BooleanProperty(default_value=False, required=False)

    def __unicode__(self):
        return 'Run: {} Group No: {}'.format(self.run_slug, self.group_no)

    class Meta:
        use_db = 'dynamodb'
        handler = docb_handler


class LoadTestResponse(docb.Document):
    project_slug = docb.SlugProperty(required=True, global_index=True)
    run_slug = docb.SlugProperty(required=True)
    path = docb.CharProperty(required=True, global_index=True)
    body = docb.CharProperty()
    user_no = docb.IntegerProperty()
    group_no = docb.IntegerProperty()
    elapsed_time = docb.FloatProperty()
    contains_string = docb.CharProperty()
    status_code = docb.IntegerProperty(required=True)
    method_type = docb.CharProperty()

    def __unicode__(self):
        return 'Run: {} Group No: {} User No: {}'.format(self.run_slug, self.group_no, self.user_no)

    class Meta:
        use_db = 'dynamodb'
        handler = docb_handler



def run_to_json(obj):
    obj.date_created = str(obj._data.pop('date_created'))
    obj.last_updated = str(obj._data.pop('last_updated'))
    return obj._data


@app.route('/', cors=True)
def projects():
    qs = Run.objects().all()

    return {
        'items': list(set([i.project_slug for i in qs]))
    }


@app.route('/project/{project_slug}', cors=True)
def get_project(project_slug):
    qs = Run.objects().filter({'project_slug': project_slug})
    return {
        'item': {
            'req_per_sec': qs.mean('requests_per_second'),
        }
    }


@app.route('/project/{project_slug}/runs', cors=True)
def get_runs(project_slug):
    qs = Run.objects().filter({'project_slug': project_slug}, sort_reverse=True, sort_attr='date_created')
    return {
        'items': [run_to_json(i) for i in qs]
    }


@app.route('/run/{run_slug}', cors=True)
def get_run(run_slug):
    obj = Run.objects().get({'run_slug': run_slug})
    return {
        'item': run_to_json(obj)
    }


@app.route('/run/{run_slug}/groups', cors=True)
def get_groups(run_slug):
    return {}
# @app.route('/run/{run_slug}/ltrs')
# def get_ltrs(run_slug):
#     qs = LoadTestResponse.objects().filter({'run_slug': run_slug}, limit=10)
#     return {
#         'items': [run_to_json(i) for i in qs]
#     }

@app.route('/latest-run', cors=True)
def latest_run():
    obj_list = Run.objects().all(sort_attr='date_created', sort_reverse=True)
    try:
        return {
            'item': run_to_json(obj_list[0])
        }
    except IndexError:
        return {
            'error': 'No Runs'
        }

@app.route('/latest-run/{project_slug}', cors=True)
def latest_run_project(project_slug):
    obj_list = Run.objects().filter({'project_slug':project_slug}, sort_attr='date_created', sort_reverse=True)
    try:
        return {
            'item': run_to_json(obj_list[0])
        }
    except IndexError:
        return {
            'error': 'No Runs'
        }

@app.route('/run-compare/{run_a}/{run_b}')
def compare_run(run_a, run_b):
    obj = Run.objects().get({'run_slug': run_a})
    obj_b = Run.objects().get({'run_slug': run_b})
    return {
        'item': {
            'run_a': run_to_json(obj),
            'run_b': run_to_json(obj_b)
        }
    }
