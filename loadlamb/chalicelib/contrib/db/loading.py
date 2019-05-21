from docb.loading import DocbHandler
from envs import env


def get_db_kwargs():
    kwargs = {
        'dynamodb': {
            'connection': {
                'table': 'loadlambddb'
            },
            'documents': ['loadlamb.chalicelib.contrib.db.models.Run', 'loadlamb.chalicelib.contrib.db.models.LoadTestResponse'],
            'table_config':{
                'write_capacity':2,
                'read_capacity':2
            }
        },

    }
    if env('DYNAMODB_ENDPOINT_URL'):
        kwargs['dynamodb']['config'] = {
            'endpoint_url':env('DYNAMODB_ENDPOINT_URL')
        }
        kwargs['dynamodb']['table_config'] = {
            'write_capacity': 100,
            'read_capacity': 100,
            'secondary_write_capacity': 100,
            'secondary_read_capacity': 100
        }
    return kwargs


docb_handler = DocbHandler(get_db_kwargs())
