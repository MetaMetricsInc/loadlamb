from docb.loading import DocbHandler
from envs import env

docb_handler = DocbHandler({
    'dynamodb': {
        'backend': 'docb.db.DynamoDB',
        'connection': {
            'table': env('DYNAMODB_TABLE')
        }
    }
})
