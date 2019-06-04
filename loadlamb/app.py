from chalice import Chalice
from chalicelib.contrib.db.models import Run, Group, LoadTestResponse

app = Chalice(app_name='loadlambapi')


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
    groups = [run_to_json(i) for i in Group.objects().filter({'run_slug': run_slug}, sort_attr='group_no')]
    return {
        'item': run_to_json(obj),
        'items': groups
    }


@app.route('/group/{group_id}', cors=True)
def get_group(group_id):
    group = Group.get(group_id)
    return {
        'item': run_to_json(group),
        'items': [i._data for i in LoadTestResponse.objects().filter({'run_slug': group.run_slug,
                                                                      'group_no': group.group_no})]
    }


@app.route('/ltr/{ltr_id}', cors=True)
def get_ltr(ltr_id):
    return {
        'item': LoadTestResponse.get(ltr_id)._data
    }


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
    obj_list = Run.objects().filter({'project_slug': project_slug}, sort_attr='date_created', sort_reverse=True)
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
