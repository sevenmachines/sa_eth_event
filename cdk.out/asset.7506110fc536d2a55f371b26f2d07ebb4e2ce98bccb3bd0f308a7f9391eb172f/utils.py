import boto3
import os
from werkzeug.utils import secure_filename
import simplejson as json
from flask import abort

s3_client = boto3.client('s3')
s3_bucket = os.environ.get('S3_BUCKET')
db_client = boto3.client('rds')
_debug = True

def _check_s3():
    """
    Check if S3 is available
    
    Parameters
    ----------

    Returns
    -------
        True if could S3 bucket available, False otherwise
    """
    return False if not s3_bucket else True

def _check_database(db):
    """
    Check if the database is available
    
    Parameters
    ----------
    db: Database
        Tge SQLAlcheny database object

    Returns
    -------
        True if could query database, False otherwise
    """
    from sqlalchemy import exc
    try:
        db.session.execute('SELECT 1')
        return True
    except exc.OperationalError:
        return False

def _init_database():
    """
    Initialise the database
    
    Parameters
    ----------

    Returns
    -------
    """
    from sqlalchemy_utils import create_database, database_exists
    from sqlalchemy import exc
    db_string = _get_db_string()
    if not database_exists(db_string):
        try:
            create_database(db_string)
        except exc.OperationalError:
            pass
        

def _get_db_string():
    """
    Get the database connection string
    
    Parameters
    ----------

    Returns
    -------
    String
        Connection string for the database
    """
    secret_arn = os.environ.get('DB_SECRETS_ARN')
    if secret_arn is not None and len(secret_arn) > 0:
        db_secrets = _get_db_secrets(secret_arn)
        db_host = db_secrets['host']
        db_engine = db_secrets['engine']
        db_port = db_secrets['port']
        db_username = db_secrets['username']
        db_password = db_secrets['password']
    else:
        db_host = 'localhost'
        db_username = 'admin'
        db_password = 'test'
    return 'postgresql://{}:{}@{}/ah'.format(db_username, db_password, db_host)

def _get_db_secrets(secret_name):
    """
    Get the database credentials from AWS Secrets Manager
    
    Parameters
    ----------
    secret_name : String
        Name of the secret

    Returns
    -------
    Dict
        Dictionary of database credentials
    """
    client = boto3.client('secretsmanager')
    response = client.get_secret_value(
        SecretId=secret_name,
    )
    secret_str = response['SecretString']
    abort(500, "Credentials not available") if not secret_str else True
    return json.loads(secret_str)

def _save_file(fileobj):
    """
    save a file locally
    
    Parameters
    ----------
    fileobj : Object
        file object of video

    Returns
    -------
    String
        local filename of uploaded video
    """
    filename = secure_filename(fileobj.filename)
    fileobj.save(filename)
    return filename

def _upload_file(filename):
    """
    upload a file to an S3 bucket
    
    Parameters
    ----------
    filename : String
        filename of video

    Returns
    -------
    Dict
        Response from the S3 service
    """
    abort(500, "Bucket not available") if not s3_bucket else True
    response = s3_client.upload_file(
        Bucket = s3_bucket,
        Filename=filename,
        Key=filename
    )
    return response

def _get_metadata(filename):
    """Generate metadata from a video file

    Parameters
    ----------
    filename : String
        filename of video

    Returns
    -------
    Dict
        dictionary of video metadata
    """
    import cv2
    cv2video = cv2.VideoCapture(filename)
    metadata = {
        'filename': filename,
        'height': cv2video.get(cv2.CAP_PROP_FRAME_HEIGHT),
        'width': cv2video.get(cv2.CAP_PROP_FRAME_WIDTH),
        'fps': cv2video.get(cv2.CAP_PROP_FPS)
    }
    return metadata

def _set_metadata(metadata):
    """Set a videos metadata in the database

    Parameters
    ----------
    metadata : Dict, optional
        dictionary of video metadata to add to the dictionary

    Returns
    -------
    bool
        True if successful, False otherwise
    """
    from app import db
    if db is not None:
        from models import Video
        video = Video(filename = metadata['filename'],
                      height = metadata['height'],
                      width = metadata['width'],
                      fps = metadata['fps'],)

        db.session.add(video)   
        db.session.commit()
        return True
    else:
        return False

def _metadata_exists(metadata):
    """Check metadata exists in the database

    Parameters
    ----------
    metadata : dict
        Video metadata 

    Returns
    -------
    bool
        True if can metadata key exists, False otherwise
    """
    res = _query_metadata(filename=metadata['filename'])
    if res is not None and len(res) > 0:
        return True
    else:
        return False

def _query_metadata(filename=None):
    """Return a list of metadata results from database

    Parameters
    ----------
    filename : String, optional
        Filename key to search for, all if not supplied

    Returns
    -------
    list
        list of all videos metadata dictionaries
    """
    from app import db
    if db is not None:
        from models import Video
        if filename is None:
            videos = db.session.query(Video).all()
        else:
            videos = db.session.query(Video).filter_by(filename=filename).all()
    else:
        videos = []
    return videos