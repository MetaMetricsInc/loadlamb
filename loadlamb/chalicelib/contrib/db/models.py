import docb

from .loading import docb_handler


class Project(docb.Document):
    name = docb.CharProperty(required=True)
    project_slug = docb.SlugProperty(required=True, unique=True)
    repo_url = docb.CharProperty()
    url = docb.CharProperty()

    def __unicode__(self):
        return self.name

    class Meta:
        use_db = 'dynamodb'
        handler = docb_handler


class Run(docb.Document):
    run_slug = docb.SlugProperty(global_index=True, unique=True)
    project_slug = docb.SlugProperty(global_index=True)
    requests = docb.IntegerProperty(required=False)
    requests_per_second = docb.FloatProperty(required=False)
    elapsed_time = docb.FloatProperty(required=False)
    last_updated = docb.DateTimeProperty(auto_now=True)
    date_created = docb.DateTimeProperty(auto_now_add=True)
    status_500 = docb.IntegerProperty()
    status_200 = docb.IntegerProperty()
    status_400 = docb.IntegerProperty()
    error_msg = docb.CharProperty(required=False)
    completed = docb.BooleanProperty(default_value=False, required=False)

    def __unicode__(self):
        return self.run_slug

    class Meta:
        use_db = 'dynamodb'
        handler = docb_handler


class LoadTestResponse(docb.Document):
    project_slug = docb.SlugProperty(required=True, global_index=True)
    run_slug = docb.SlugProperty(required=True)
    path = docb.CharProperty(required=True, global_index=True)
    body = docb.CharProperty()
    elapsed_time = docb.FloatProperty()
    contains_string = docb.CharProperty()
    status_code = docb.IntegerProperty(required=True)
    method_type = docb.CharProperty()

    class Meta:
        use_db = 'dynamodb'
        handler = docb_handler
