import docb

from .loading import docb_handler


class Run(docb.Document):
    run_slug = docb.SlugProperty(index=True, unique=True)
    project_slug = docb.SlugProperty(index=True)
    last_updated = docb.DateTimeProperty(auto_now=True)
    date_created = docb.DateTimeProperty(auto_now_add=True)

    def __unicode__(self):
        return self.name

    class Meta:
        use_db = 'dynamodb'
        handler = docb_handler


class LoadTestResponse(docb.Document):
    project_slug = docb.SlugProperty(required=True, index=True)
    run_slug = docb.SlugProperty(required=True)
    path = docb.CharProperty(required=True, index=True)
    elapsed_time = docb.FloatProperty()
    contains_string = docb.CharProperty()
    status_code = docb.IntegerProperty(required=True,index=True)
    method_type = docb.CharProperty()
    body = docb.CharProperty()
    headers = docb.CharProperty()

    class Meta:
        use_db = 'dynamodb'
        handler = docb_handler
