"""
app.py
---
Flask app file.
"""
import sys
import json
from quart import Quart, render_template

#DON'T GENERATE __PYCACHE__
sys.dont_write_bytecode = True

#FLASK APP
app = Quart(__name__)

@app.route("/")
async def pageHome():
    return await render_template('index.html')
