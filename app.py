import configparser
from flask import Flask

def read_ini(file_path):
    config = configparser.ConfigParser()
    config.read(file_path)
    return config

app = Flask(__name__)
config = read_ini("config.ini")
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = 'static/uploads/'
app.config['SUMMARY_FOLDER'] = 'static/summaries/'
app.config['PROCESS_FOLDER'] = 'static/processing/'
app.config['CHECKPOINT'] = 'models/DSNet/checkpoints/ours.yml.2.pt'
app.config['DEVELOPMENT'] = 'True'
app.config['MAX_CONTENT_LENGTH'] = None #16 * 1024 * 1024 # 16MBs

