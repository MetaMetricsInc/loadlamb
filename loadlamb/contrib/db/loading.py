from docb.loading import DocbHandler
from envs import env

docb_handler = DocbHandler({
    'dynamodb': {
        'backend': 'docb.backends.dynamodb.db.DynamoDB',
        'connection': {
            'table': env('DYNAMODB_TABLE')
        }
    }
})