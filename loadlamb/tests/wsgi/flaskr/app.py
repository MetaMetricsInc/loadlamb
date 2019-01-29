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
