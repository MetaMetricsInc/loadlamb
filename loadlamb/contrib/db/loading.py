from docb.loading import DocbHandler
from envs import env


def get_db_kwargs():
    kwargs = {
        'dynamodb': {
            'connection': {
                'table': env('DYNAMODB_TABLE')
            }
        },
        'documents': ['loadlamb.contrib.db.models.Run','loadlamb.contrib.db.models.LoadTestResponse']
    }
    if env('DYNAMODB_ENDPOINT_URL'):
        kwargs['config'] = {
            'endpoint_url':'http://localhost:8000'
        }
        kwargs['table_config'] = {
            'write_capacity': 100,
            'read_capacity': 100,
            'secondary_write_capacity': 100,
            'secondary_read_capacity': 100
        }
    return kwargs


docb_handler = DocbHandler({
    'dynamodb': {
        'connection': {
            'table': env('DYNAMODB_TABLE')
        }
    }
})