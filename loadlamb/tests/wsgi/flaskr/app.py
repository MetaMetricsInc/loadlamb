from flask import Flask, jsonify
from flask.views import View
app = Flask(__name__)


class MethodView(View):
    methods = ['GET', 'POST']

    def dispatch_request(self):
        return jsonify(success='ok')


class Get(MethodView):
    methods = ['GET']


app.add_url_rule('/get', view_func=Get.as_view('get'))


class Post(MethodView):
    methods = ['POST']


app.add_url_rule('/post', view_func=Post.as_view('post'))


class BadGet(MethodView):
    methods = ['GET']

    def dispatch_request(self):
        response = jsonify(success='no')
        response.status_code = 500
        return response

app.add_url_rule('/bad-get', view_func=BadGet.as_view('bad-get'))