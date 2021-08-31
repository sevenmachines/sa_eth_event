import flask
from flask import Flask, render_template, request, redirect, send_file, jsonify, abort
from config import Config
from flask_sqlalchemy import SQLAlchemy
import simplejson as json
import os
import utils
from flask_migrate import Migrate

def _create_app():
    """
    Create the flask application
    """
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config.from_object(os.environ.get('APP_SETTINGS'))
    return app

def _create_db(app):
    """
    Create the database and migrations
    """
    db = SQLAlchemy(app)
    migrate = Migrate(app, db)
    db.init_app(app)
    utils._init_database()
    return db

app = _create_app()
db = _create_db(app)

@app.route('/')
def index():
    """
    Main page to upload files and display the list of metadata
    """
    contents = utils._query_metadata()
    return flask.render_template('index.html',
                                 bucket_name=utils.s3_bucket,
                                 contents=contents)


@app.route("/upload", methods=['POST'])
def upload():
    """
    Upload a file to s3 and set the metadata in the database
    """
    if request.method == "POST":
        fileobj = request.files['file']
        if fileobj:
            filename = utils._save_file(fileobj)
            metadata = utils._get_metadata(filename)
            if not utils._metadata_exists(metadata):
                utils._upload_file(filename)
                utils._set_metadata(metadata)
    return redirect("/")
    
@app.route("/list",  methods=['GET'])
def list():
    """
    List the metadata in the database
    """
    if request.method == "GET":
        serialised_data = [video.serialise() for video in utils._query_metadata()]
        return jsonify(serialised_data)

@app.route("/health", methods=['GET'])
def health():
    """
    Check health and connectivity. Note, this is a machine-automation endpoint 
    for application destruction
    """
    if not utils._check_database(db):
        return "No database connection", 504 
    elif not utils._check_s3():
        return "Missing S3 bucket storage", 504 
    return "OK", 200
