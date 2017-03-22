# ITA Survey of International Air Travelers (SIAT) Lambda

This project provides an AWS Lambda that transforms SIAT Excel spreadsheets into a CSV file for endpoint-me. 

## Prerequisites

Follow instructions from [python-lambda](https://github.com/nficano/python-lambda) to ensure your basic development environment is ready,
including:

* Python
* Pip
* Virtualenv
* Virtualenvwrapper
* AWS credentials

## Getting Started

  git clone git@github.com:GovWizely/lambda-siat.git
  cd lambda-siat
  mkvirtualenv -r requirements.txt lambda-siat

## Configuration

* Define AWS credentials in either `config.yaml` or in the [default] section of ~/.aws/credentials.
* Edit `config.yaml` if you want to specify a different AWS region, role, and so on.
* Make sure you do not commit the AWS credentials to version control

## Invocation

  lambda invoke -v
 
## Deploy

  lambda deploy
