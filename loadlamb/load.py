import requests

from loadlamb.request import Request
from loadlamb.utils import import_util

METHOD_TYPES = ['get','post','put','head','delete']


class LoadLamb(object):

    def __init__(self, config):
        self.config = config

    def run(self):
        s = requests.Session()
        responses = []
        for i in self.config['tasks']:
            if i.get('method_type','').lower() in METHOD_TYPES and not i.get('request_class'):
                r = Request(s,i,self.config)
                rs = r.run()
                responses.append(rs)
                s = r.session
            else:
                r = import_util(i.get('request_class'))(s,i,self.config)
                rs = r.run()
                if isinstance(rs,(list,tuple,set)):
                    responses.extend(rs)
                else:
                    responses.append(rs)
                s = r.session
        return responses