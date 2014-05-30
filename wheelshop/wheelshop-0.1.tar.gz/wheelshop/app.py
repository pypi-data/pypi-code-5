import boto
import os
from flask import Flask, redirect
from wheel.install import WheelFile

app = Flask(__name__)

conn = boto.connect_s3()
bucket = conn.get_bucket(os.environ.get('WHEELSHOP_S3_BUCKET'))

def check_package_match(file_pkg_name, request_pkg_name, version=None):
    if not version:
        search_string = request_pkg_name.lower().replace("-", "_")
        normalized_filename = "%s" % file_pkg_name.split("-")[0].lower().replace("-", "_")
        return search_string == normalized_filename
    else:
        search_string = request_pkg_name.lower().replace("-", "_")
        normalized_filename = "%s" % file_pkg_name.split("-")[0].lower().replace("-", "_")
        return search_string == normalized_filename and version == file_pkg_name.split("-")[1]

@app.route("/")
def index():
    return "".join(["<a href='/%(package)s/'>%(package)s</a><br />" % {'package': WheelFile(pkg).parsed_filename.group('name')} for pkg in sorted(set([k.key for k in bucket.list(delimiter="/")]))])

@app.route('/<package_name>/')
def package(package_name):
    return "".join(["<a rel='internal' href='/dl/%s'>%s</a><br />" % (pkg, pkg) for pkg in [k.key for k in bucket.list(delimiter="/")] if check_package_match(pkg, package_name)])


@app.route('/<package_name>/<version>')
def package_with_version(package_name, version):
    return "".join(["<a rel='internal' href='/dl/%s'>%s</a><br />" % (pkg, pkg) for pkg in [k.key for k in bucket.list(delimiter="/")] if check_package_match(pkg, package_name, version)])

@app.route('/dl/<filename>')
def get_file(filename):
    return redirect(bucket.get_key(filename).generate_url(expires_in=300))

if __name__ == "__main__":
    app.run(port=5000, host="0.0.0.0")
