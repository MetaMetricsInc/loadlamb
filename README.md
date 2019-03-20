# loadlamb

A load testing util built to run on AWS Lambda with SQS and DynamoDB.

## Current Status

Alpha

## Install

```python    
pip install loadlamb
```

## Project Goals

1. Easy load testing from CI/CD pipeline
2. Easily readable results via UI
3. Test our AWS powered apps as close as possible to the deployment region as possible
4. Request workers should run cheaply and only on demand on AWS Lambda.
5. Configuration should be *MOSTLY** programming language agnostic. So developers, engineers, QA teams alike can use it. 
6. Keep a persistent record of the test results. This is important so action can be taken if code is pushed that drastically reduces performance.
7. Extendable with for different workflows (remote login, OpenID, API auth, and etc.)

## How it Works (currently)

**IMPORTANT:** Remember this project is still in its alpha stage. 

### Execute/SQS Push

Currently, the load test kicks off by the CLI invoking the **"Push"** AWS Lambda function sending the config to the function as the event. This function sends the config to the SQS Queue the same number times specified in the **user_num** attribute. 

### Pull messages from SQS/Make Requests

This triggers the **"Pull"** Lambda function, and it makes the requests from the tasks section of the project's config using the Requests library's Session class via the [Request](#request-class) class (loadlamb.request.Request). This happens independently for each user specified in user_num. For example, if you specify 500 users then 500 SQS messages will be sent, triggering 500 Lambdas, which means the tasks will be run 500 times with different sessions. 

### Save Data

After all of the requests are made we save the results in DynamoDB.
   

## CLI

These commands and the project should be created in your project's code repository so you can use your CI/CD toools (travis, circleci, bitbucket pipelines, etc.) to kick off the test when new code is introduced. The CLI assumes you have credentials stored at **~/.aws/credentials** or wherever your OS stores them.

### Essential Commands

#### Create a New Project

This command creates will ask you a few questions and then create a file named **loadlamb.yaml** that stores those answers along with a sample request.
 
```bash
loadlamb create_project
```

#### Create a New Extension

This command creates a new extension. This is useful for creating new request types and tasks that need more than one request.

```bash
loadlamb create_extension
``` 

#### Deploy LoadLamb

This command zips the requirement libraries, the core loadlamb code, custom extension, and uses a SAM template to deploy the Lambda functions (push_handler and pull_handler), DynamoDB table, SQS message, and a new role via CloudFormation.

```bash
loadlamb deploy
```

#### Run LoadLamb

This command uses boto3 to execute the **push_handler** Lambda function by using the contents of the **loadlamb.yaml** as the event (payload) argument. Which sends the config as an SQS message. 
```bash
loadlamb execute
```

### Non-Essential Commands 
#### Create the SAM Template

This command creates a SAM template named **sam.yml**.

```bash
loadlamb create_template
```
#### Create the Code's Zip File

This command zips the requirement libraries, the core loadlamb code, and custom extensions up in a zip file.

```bash
loadlamb create_package
```

## Anatomy of the LoadLamb.yaml Config File

### Example File

```yaml
bucket: your_bucket # The bucket the code (loadlamb.zip) will be uploaded to.
name: your_project_name # The name of the project
url: https://example.org # The base url of the site you're testing
user_num: 50 # The number of users to simulate
user_batch_size: 10 # The number of users we create at a time. Value should be from 1-10
tasks: # Lists of tasks for each simulated user
- path: / # The path on the site for the request 
  method_type: GET # The HTTP method that should be used
  contains: Welcome # Test to make sure the specified text appears on the page
- path: /login/
  request_class: loadlamb.contrib.requests.login.RemoteLogin
  users:
  - username: your_user
    password: your_password
  - username: your_user2
    password: your_password
- path: /account/profile/
  method_type: GET
  contains: My Profile
  payload:
  - some_url_var: test
  - some_url_var: test-b
- path: /account/profile/update/
  method_type: POST
  contains: Update My Profile
  data:
  - username: brian
    address: 123 Any Ln
  - username: mikejordan
    address: 123 Broad St
```

## Request and Response Classes

### Request Class

The **Request** (loadlamb.request.Request) class is essentially a wrapper around the [Requests ](http://docs.python-requests.org/en/master/) library's Session class. This Session object is passed around from task to task in the Lambda function that pulls from the SQS queue. The easiest way to dissect this is to just look at the code. Below is the current Request class.    
```python
class Request(object):

    def __init__(self,session, req_config, proj_config, **kwargs):
        self.req_config = req_config
        self.proj_config = proj_config
        self.kwargs = kwargs
        self.session = session

    def run(self):
        path = '{}{}'.format(self.proj_config.get('url'),
                             self.req_config.get('path'))
        method_type = self.req_config.get('method_type')
        data = self.req_config.get('data')
        payload = self.req_config.get('payload')

        timeout = self.req_config.get('timeout') or \
                  self.proj_config.get('timeout',30)
        if data:
            data = self.get_choice(data)
            resp = self.session.request(method_type,path,data=data,timeout=timeout)
        elif payload:
            payload = self.get_choice(payload)
            resp = self.session.request(method_type, path, timeout=timeout, payload=payload)
        else:
            resp = self.session.request(method_type, path, timeout=timeout)
        return Response(resp,self.req_config,
                        self.proj_config.get('project_slug'),
                        self.proj_config.get('run_slug'))

    def get_choice(self,choice_list):
        return random.choice(choice_list)
```

#### Subclassing the Request Class 

If you want to create a new Request class in your extension there are only one method that is required. That is the **run** method.

### Response Class

At this point the main purpose of the Response class is to save the result to DynamoDB. In the future you will be able to subclass it and specify a new class in the config.