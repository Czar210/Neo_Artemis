import requests
import os
from dotenv import load_dotenv
import json
import pandas as pd
import time
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
import csv
import re
load_dotenv()
API_KEY = os.getenv("API_KEY")

API_KEYS = []
i = 1
while True:
    key = os.getenv(f"API_KEY_{i}")
    if not key:
        break
    API_KEYS.append(key)
    i += 1

print('------------------------------------------------------------------------')

