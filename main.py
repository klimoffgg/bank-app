from fastapi import FastAPI, status, HTTPEcxeption
from pydantic import Basemodel

class TransactionStatus (Basemodel):
    DRAFT = 'DRAFT'
    PROCESSING = 'PROCESSING'
    FROZEN = 'FROZEN'
    ARCHIVE = 'ARCHIVE'

class TransactionCreate (Basemodel):
