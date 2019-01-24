import docb

from chalice import Chalice

app = Chalice(app_name='loadlambapi')

docb_handler = docb.loading.DocbHandler({
        'dynamodb': {
            'connection': {
                'table': 'loadlambddb'
            },
            'table_config':{
                'write_capacity':2,
                'read_capacity':2
            }
        },

    })


class Run(docb.Document):
    run_slug = docb.SlugProperty(global_index=True, unique=True)
    project_slug = docb.SlugProperty(global_index=True)
    requests = docb.IntegerProperty(required=False, default_value=1)
    requests_per_second = docb.FloatProperty(required=False, default_value=1)
    elapsed_time = docb.FloatProperty(required=False, default_value=1)
    last_updated = docb.DateTimeProperty(auto_now=True)
    date_created = docb.DateTimeProperty(auto_now_add=True)

    def __unicode__(self):
        return self.name

    class Meta:
        use_db = 'dynamodb'
        handler = docb_handler


class LoadTestResponse(docb.Document):
    project_slug = docb.SlugProperty(required=True, global_index=True)
    run_slug = docb.SlugProperty(required=True)
    path = docb.CharProperty(required=True, global_index=True)
    elapsed_time = docb.FloatProperty()
    contains_string = docb.CharProperty()
    status_code = docb.IntegerProperty(required=True)
    method_type = docb.CharProperty()

    class Meta:
        use_db = 'dynamodb'
        handler = docb_handler


def run_to_json(obj):
    obj.date_created = str(obj._data.pop('date_created'))
    obj.last_updated = str(obj._data.pop('last_updated'))
    return obj._data


@app.route('/')
def projects():
    qs = Run.objects().all()
    return {
        'items': list(set([i.project_slug for i in qs]))
    }


@app.route('/{project_slug}')
def get_project(project_slug):
    qs = Run.objects().filter({'project_slug': project_slug})
    return {
        'item':{
            'req_per_sec': qs.mean('requests_per_second'),
        }
    }


@app.route('/run/{run_slug}')
def get_run(run_slug):
    obj = Run.objects().get({'run_slug': run_slug})
    return {
        'item': run_to_json(obj)
    }


@app.route('/run-compare/{run_a}/{run_b}')
def compare_run(run_a,run_b):
    obj = Run.objects().get({'run_slug': run_a})
    obj_b = Run.objects().get({'run_slug': run_b})
    return {
        'item': {
            'run_a': run_to_json(obj),
            'run_b': run_to_json(obj_b)
        }
    }