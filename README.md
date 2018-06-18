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

### Create a New Project


### Deploy LoadLamb


### Run LoadLamb


## Request and Response Classes

