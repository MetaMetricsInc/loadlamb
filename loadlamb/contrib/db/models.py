import docb

from .loading import docb_handler


class LoadTest(docb.Document):
    name = docb.CharProperty(required=True, unique=True)
    slug = docb.SlugProperty(index=True,unique=True)
    last_updated = docb.DateTimeProperty(auto_now=True)
    date_created = docb.DateTimeProperty(auto_now_add=True)

    def __unicode__(self):
        return self.name

    class Meta:
        use_db = 'dynamodb'
        handler = docb_handler


class Path(docb.Document):
    project_slug = docb.SlugProperty(required=True, index=True)
    slug = docb.SlugProperty(required=True,index=True)

    class Meta:
        use_db = 'dynamodb'
        handler = docb_handler


class LoadTestRequest(docb.Document):
    project_slug = docb.SlugProperty(required=True, index=True)
    path = docb.CharProperty(required=True, index=True)
    elapsed_time = docb.IntegerProperty()
    assertion_pass = docb.BooleanProperty()
    contains_string = docb.CharProperty()
    status_code = docb.IntegerProperty()
    response_size = docb.IntegerProperty()
    method_type = docb.CharProperty()

    class Meta:
        use_db = 'dynamodb'
        handler = docb_handler
