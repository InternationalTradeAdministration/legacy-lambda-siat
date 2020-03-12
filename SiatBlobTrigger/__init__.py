import logging

import azure.functions as func
from pathlib import Path
import os, uuid, urllib, xlrd, re
from azure.storage.blob import BlobServiceClient, ContainerClient, BlobClient
from .service import handler

def main(myblob: func.InputStream):

    logging.info(f"Python blob trigger function processed blob \n"
                 f"Name: {myblob.name}\n"
                 f"Blob Size: {myblob.length} bytes")
    
    fileToConvert = myblob
    
    blob_uri = myblob.uri

    blob_path, headers = urllib.request.urlretrieve(blob_uri)
    blob_service_client = BlobServiceClient(account_url = blob_uri, credential=None)

    if ".xlsx" in myblob.name:
        handler(blob_path, myblob.name, blob_uri)