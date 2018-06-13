from docb.loading import DocbHandler


docb_handler = DocbHandler({
    'dynamodb': {
        'backend': 'docb.backends.dynamodb.db.DynamoDB',
        'connection': {
            'table': 'your-dynamodb-table',
        }
    }
})