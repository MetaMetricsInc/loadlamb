from docb.loading import DocbHandler
from envs import env

docb_handler = DocbHandler({
    'dynamodb': {
        'connection': {
            'table': env('DYNAMODB_TABLE')
        }
    }
})