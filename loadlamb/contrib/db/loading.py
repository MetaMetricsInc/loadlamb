from docb.loading import DocbHandler
from envs import env

docb_handler = DocbHandler({
    'dynamodb': {
        'backend': 'docb.db.DynamoDB',
        'connection': {
            'table': env('DYNAMODB_TABLE')
        },
        'config': {
            'write_capacity':5,
            'read_capacity':5,
            'secondary_write_capacity':5,
            'secondary_read_capacity':5
        }
    }
})
