from docb.loading import DocbHandler
from envs import env


def get_db_kwargs():
    kwargs = {
        'dynamodb': {
            'connection': {
                'table': 'loadlambddb'
            },
            'config': {
                'endpoint_url':'http://dynamodb:8000'
            },
            'documents': ['loadlamb.contrib.db.models.Run', 'loadlamb.contrib.db.models.LoadTestResponse'],
            'table_config':{
                'write_capacity':2,
                'read_capacity':2
            }
        },

    }
    print('Got Here Before')
    if env('DYNAMODB_ENDPOINT_URL'):
        print('Got Here After')
        kwargs['dynamodb']['config'] = {
            'endpoint_url':'http://dynamodb:8000'
        }
        kwargs['dynamodb']['table_config'] = {
            'write_capacity': 100,
            'read_capacity': 100,
            'secondary_write_capacity': 100,
            'secondary_read_capacity': 100
        }
    return kwargs


docb_handler = DocbHandler(get_db_kwargs())
