import os
import sys

sys.path.append(os.getcwd())

import json

from app import create_app, db

from app.models import WifiNetwork

app = create_app("development")
app_context = app.app_context()
app_context.push()