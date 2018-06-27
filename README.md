# loadlamb

A load testing util built to run on AWS Lambda with Kinesis and DynamoDB.

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

## CLI

These commands and the project should be created in your project's code repository so you can use your CI/CD toools (travis, circleci, bitbucket pipelines, etc.) to kick off the test when new code is introduced. The CLI assumes you have credentials stored at **~/.aws/credentials** or wherever your OS stores them.

### Create a New Project

This command creates will ask you a few questions and then create a file named **loadlamb.yaml** that stores those answers along with a sample request.
 
```bash
loadlamb create_project
```

### Deploy LoadLamb

This command uses a SAM template to deploy the Lambda functions (push_handler and pull_handler), DynamoDB table, SNS topic (this will be replaced by SQS when SQS becomes an event source), and a new role via CloudFormation.

```bash
loadlamb deploy
```

### Run LoadLamb

This command uses boto3 to execute the **push_handler** Lambda function by using the contents of the **loadlamb.yaml** as the event (payload) argument. Which sends the config as an SNS (this will change to SQS in the future) message the number. 
```bash
loadlamb execute
```

## Anatomy of the LoadLamb.yaml Config File

### Example File

```yaml
bucket: your_bucket # The bucket the code (loadlamb.zip) will be uploaded to.
name: your_project_name # The name of the project
url: https://example.org # The base url of the site you're testing
user_num: 50 # The number of users to simulate
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

