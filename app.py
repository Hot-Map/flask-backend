import configparser
from flask import Flask

def read_ini(file_path, app):
    config = configparser.ConfigParser()
    config.read(file_path)

    for section in config.sections():
        print()
        if section == 'BASIC':
            for k, v in config[section].items():
                print(k, v, type(v))
                if v == 'None':
                    v = None
                app.config[k.upper()] = v
        else:
            s = {}
            for k, v in config[section].items():
                if v == 'None':
                    v = None
                s[k.upper()] = v
            app.config[section] = s

    print("fianl")
    for k, v in app.config.items():
        print(k, v, type(v))
    return config

app = Flask(__name__)
read_ini("config.ini", app)

