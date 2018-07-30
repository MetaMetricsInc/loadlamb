from setuptools import setup, find_packages


def parse_requirements(filename):
    """ load requirements from a pip requirements file """
    lineiter = (line.strip() for line in open(filename))
    return [line for line in lineiter if line and not line.startswith("#")]


setup(
    name='loadlamb',
    description='A load testing util built to run on AWS Lambda with Kinesis and DynamoDB',
    url='https://github.com/capless/loadlamb',
    author='Brian Jinwright',
    license='GNU GPL v3',
    keywords='load testing, lambda',
    install_requires=parse_requirements('requirements.txt'),
    packages=find_packages(),
    include_package_data=True,
    version='0.3.1a',
    entry_points='''
        [console_scripts]
        loadlamb=loadlamb.cli:loadlamb
        ''',
)
