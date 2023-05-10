from flask import Flask

app = Flask(__name__)
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = 'static/uploads/'
app.config['SUMMARY_FOLDER'] = 'static/summaries/'
app.config['CHECKPOINT'] = 'models/DSNet/checkpoints/ours.yml.2.pt'
app.config['MAX_CONTENT_LENGTH'] = None #16 * 1024 * 1024 # 16MBs