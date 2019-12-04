from flask import Flask, request

from icd_reader.classes.HtmlParser import HtmlParser
from icd_reader.classes.IcdMapper import IcdMapper
from icd_reader.classes.IcdWikipediaMapper import IcdWikipediaMapper
from icd_reader.classes.WikipediaClient import WikipediaClient

app = Flask(__name__)

@app.route('/')
def icd_reader():
    return 'This is ICD Reader'

@app.route('/map', methods=['POST', 'PUT'])
def add_or_update():
    if request.method == 'POST':
        return 'Im map route POST'
    elif request.method == "PUT":
        return 'Im map route PUT'

@app.route('/icd-10/<code>', methods=['GET'])
def get_icd10(code: str):
    return 'Im icd-10 {}'.format(code)

@app.route('/icd-10/<code>/<subcode>', methods=['GET'])
def get_icd10_sub(code: str, subcode: str):
    return 'Im icd-10 {}'.format(code + " " + subcode)

@app.route('/icd-11/<code>', methods=['GET'])
def get_icd11(code: str):
    return 'Im icd-11 {}'.format(code)

@app.route('/icd-11/<code>/<subcode>', methods=['GET'])
def get_icd11_sub(code: str, subcode: str):
    return 'Im icd-11 {}'.format(code + " " + subcode)

if __name__ == '__main__':
    app.run()