from utils import Utils
from __main__ import app

@app.route('/')
def index():
    contents = Utils._query_metadata()
    return flask.render_template('index.html',
                                 bucket_name=Utils.s3_bucket,
                                 contents=contents)


@app.route("/upload", methods=['POST'])
def upload():
    if request.method == "POST":
        fileobj = request.files['file']
        if fileobj:
            filename = Utils._save_file(fileobj)
            metadata = Utils._get_metadata(filename)
            if not Utils._metadata_exists(metadata):
                Utils._upload_file(filename)
                Utils._set_metadata(metadata)
    return redirect("/")
    
@app.route("/list",  methods=['GET'])
def list():
    if request.method == "GET":
        return jsonify(Utils._query_metadata())

@app.route("/health", methods=['GET'])
def health():
    return "OK", 200