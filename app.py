import json
import configparser
from flask import Flask

def filter_dictionary(dictionary):
    filtered_dict = {}
    for key, value in dictionary.items():
        try:
            json.dumps(value)
            filtered_dict[key] = value
        except Exception as e:
            filtered_dict[key] = str(value)
    return filtered_dict

def read_ini(file_path, app):
    config = configparser.ConfigParser()
    config.read(file_path)
    for section in config.sections():
        if section == 'BASIC':
            for k, v in config[section].items():
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
    return config

def set_config(app):
    read_ini("config.ini", app)

app = Flask(__name__)
set_config(app)


