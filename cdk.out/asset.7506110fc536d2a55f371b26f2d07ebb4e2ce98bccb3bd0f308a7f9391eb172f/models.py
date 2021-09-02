from app import db
import simplejson as json

class Video(db.Model):
    """
    Model for video metadata
    """
    __tablename__ = 'videos'

    filename = db.Column(db.String(), primary_key=True)
    height = db.Column(db.Integer, unique=False, nullable=False)
    width = db.Column(db.Integer, unique=False, nullable=False)
    fps = db.Column(db.Numeric(precision=2), unique=False, nullable=False)

    def __init__(self, filename, height, width, fps):
        self.filename = filename
        self.height = height
        self.width = width
        self.fps = fps

    def serialise(self):
        return ({"filename": self.filename,
                "height": int(self.height),
                "width": int(self.width),
                "fps": int(self.fps)})

    def __repr__(self):
        return '<filename {}>'.format(self.filename)
