# ITA Survey of International Air Travelers (SIAT) Azure Function

This project provides an Azure Function that transforms SIAT Excel spreadsheets into a CSV file for endpoint-me.

## Prerequisites

Follow instructions from [python-lambda](https://github.com/nficano/python-lambda) to ensure your basic development environment is ready,
including:

* Python v3.6.9
* Pip
* Virtualenv
* Virtualenvwrapper
* Azure credentials

## Getting Started

  `git clone https://github.com/InternationalTradeAdministration/siat-translator.git`
  `cd siat-translator`
  `mkvirtualenv -r requirements.txt lambda-siat`
  `source /path/to/venv/bin/activate`

## Configuration

* You must have an Azure account and a storage account.
* Create a function app at portal.azure.com, ensure you make an application setting called AzureStorageKey using a key from your storage account
* Refer to deploy section for instructions on how to deploy to Azure
* Create a container in your storage account and change the path in function.json as needed

If using Visual Studio Code, you will need to install the following:

* Azure Account
* Azure App Service
* Azure CLI Tools
* Azure Functions
* Azure Storage

## Run Locally

  `func host start`

You can upload Microsoft Excel files with the .xlsx extension to the container you specified in function.json. The function is triggered by new blobs that are uploaded into the specified container. After the conversion is done, a directory called translated will appear in the specified container and will hold the converted files.
