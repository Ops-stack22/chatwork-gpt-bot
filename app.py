from flask import Flask, request, jsonify
import json
import base64
from oauth2client.service_account import ServiceAccountCredentials
import gspread
import openai


