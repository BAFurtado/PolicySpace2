from flask import Flask
from . import api, web

app = Flask(
    __name__,
    static_url_path='/assets',
    static_folder='static',
    template_folder='templates')

app.config['SECRET_KEY'] = 'secret' # this is fine if running locally
app.register_blueprint(api.bp)
app.register_blueprint(web.bp)
