import docb

from .loading import docb_handler


class Project(docb.Document):
    name = docb.CharProperty(required=True)
    project_slug = docb.SlugProperty(required=True, unique=True)
    repo = docb.CharProperty()
    deployment_type = docb.SlugProperty()

    def __unicode__(self):
        return self.name

    class Meta:
        use_db = 'dynamodb'
        handler = docb_handler


class Stage(docb.Document):
    name = docb.CharProperty(required=True)
    project_slug = docb.SlugProperty(required=True)
    url = docb.CharProperty()
    branch = docb.CharProperty(required=True)
    last_modified = docb.DateTimeProperty(auto_now_add=True)

    class Meta:
        use_db = 'dynamodb'
        handler = docb_handler


class Run(docb.Document):
    run_slug = docb.SlugProperty(global_index=True, unique=True)
    stage = docb.SlugProperty()
    project_slug = docb.SlugProperty(global_index=True)
    requests = docb.IntegerProperty(required=False)
    requests_per_second = docb.FloatProperty(required=False)
    elapsed_time = docb.FloatProperty(required=False)
    commit = docb.CharProperty(required=False)
    last_updated = docb.DateTimeProperty(auto_now=True)
    date_created = docb.DateTimeProperty(auto_now_add=True)
    user_batch_size = docb.IntegerProperty(required=False)
    user_batch_sleep = docb.IntegerProperty(required=False)
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


class Group(docb.Document):
    run_slug = docb.SlugProperty(global_index=True)
    project_slug = docb.SlugProperty(global_index=True)
    group_no = docb.IntegerProperty(required=True)
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
        return 'Run: {} Group No: {}'.format(self.run_slug, self.group_no)

    class Meta:
        use_db = 'dynamodb'
        handler = docb_handler


class LoadTestResponse(docb.Document):
    project_slug = docb.SlugProperty(required=True, global_index=True)
    run_slug = docb.SlugProperty(required=True)
    path = docb.CharProperty(required=True, global_index=True)
    body = docb.CharProperty()
    user_no = docb.IntegerProperty()
    group_no = docb.IntegerProperty()
    elapsed_time = docb.FloatProperty()
    contains_string = docb.CharProperty()
    status_code = docb.IntegerProperty(required=True)
    method_type = docb.CharProperty()

    def __unicode__(self):
        return 'Run: {} Group No: {} User No: {}'.format(self.run_slug, self.group_no, self.user_no)

    class Meta:
        use_db = 'dynamodb'
        handler = docb_handler
