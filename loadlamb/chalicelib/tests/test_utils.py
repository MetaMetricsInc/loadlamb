import os
import shutil

from loadlamb.chalicelib.utils import grouper, import_util, save_sam_template, read_config_file, create_config_file, \
    create_extension_template

from docb import Document

TEST_CONFIG = {
        'name': 'flask',
        'url': 'http://flask:5000',
        'repo': 'loadlamb',
        'user_num': 10,
        'user_batch_size': 10,
        'user_batch_sleep': 2,
        'tasks': [
            {'path': '/get', 'method_type': 'GET'},
            {'path': '/post', 'method_type': 'POST'},
            {'path': '/bad-get', 'method_type': 'GET'},
        ]
    }


def test_grouper():
    g = grouper(5, 38)
    assert g == [5, 5, 5, 5, 5, 5, 5, 3]


def test_import_util():
    u = import_util('loadlamb.chalicelib.contrib.db.models.Run')
    assert issubclass(u, Document)


def test_save_sam_template():
    save_sam_template()
    assert os.path.isfile('sam.yml')
    os.remove('sam.yml')


def test_create_read_config():
    create_config_file(config=TEST_CONFIG)
    assert os.path.isfile('loadlamb.yaml')
    assert read_config_file('loadlamb.yaml') == TEST_CONFIG
    os.remove('loadlamb.yaml')


def test_create_extension_template():
    create_config_file(config=TEST_CONFIG)
    create_extension_template('jelly', 'Test extension')
    assert read_config_file('loadlamb.yaml') == {'name': 'flask',
                                                 'repo': 'loadlamb',
                                                 'tasks': [{'method_type': 'GET', 'path': '/get'},
                                                           {'method_type': 'POST', 'path': '/post'},
                                                           {'method_type': 'GET', 'path': '/bad-get'}],
                                                 'url': 'http://flask:5000', 'user_batch_size': 10,
                                                 'user_batch_sleep': 2, 'user_num': 10, 'extensions': ['jelly']}
    shutil.rmtree('jelly')

