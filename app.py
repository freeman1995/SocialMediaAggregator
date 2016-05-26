from bottle import run
from presentation.controller.controller import app

run(app, host='localhost', port=8080)
