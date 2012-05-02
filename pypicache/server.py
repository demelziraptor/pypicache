import logging
import mimetypes
import re

import bottle

from pypicache import cache

CACHE = None

app = bottle.Bottle()

@app.route("/")
def index():
    return "Index not baked yet, try /simple/<package>/"

@app.route("/simple")
@app.route("/simple/")
def simple_index():
    """The top level simple index page

    """
    return "Not done yet, try /simple/<package>"

@app.route("/simple/<package>")
@app.route("/simple/<package>/")
def pypi_simple_package_info(package):
    return CACHE.pypi_get_simple_package_info(package)

@app.route("/local/<package>")
@app.route("/local/<package>/")
def local_simple_package_info(package):
    return CACHE.local_get_simple_package_info(package)

@app.route("/packages/source/<firstletter>/<package>/<filename>", "GET")
def get_sdist(firstletter, package, filename):
    try:
        content_type, _ = mimetypes.guess_type(filename)
        logging.debug("Setting mime type of {!r} to {!r}".format(filename, content_type))
        bottle.response.content_type = content_type
        return CACHE.get_sdist(package, filename)
    except cache.NotFound:
        return bottle.NotFound()

@app.route("/packages/source/<firstletter>/<package>/<filename>", "PUT")
def put_sdist(firstletter, package, filename):
    """

    Upload using:

    curl -X PUT --data-binary @dist/mypackage-1.0.tar.gz http://localhost:8080/packages/source/m/mypackage/mypackage-1.0.tar.gz

    """
    CACHE.add_sdist(package, filename, bottle.request.body)
    return {"uploaded": "ok"}

@app.route("/uploadpackage/<filename>", "POST")
def post_sdist(filename):
    """

    POST using:

    curl -X POST --data-binary @dist/mypackage-1.0.tar.gz http://localhost:8080/uploadpackage/mypackage-1.0.tar.gz

    """
    # TODO parse package versions properly, hopefully via distutils2 style library
    # Assume package in form <package>-<version>.tar.gz
    package = re.match(r"(?P<package>.*?)-.*?\..*", filename).groupdict()["package"]
    logging.debug("Parsed {!r} out of {!r}".format(package, filename))
    return CACHE.add_sdist(package, filename, bottle.request.body)

@app.route("/requirements.txt", "POST")
def POST_requirements_txt():
    """POST a requirements.txt to get the packages therein

    Works best with:

    pip freeze | curl  -X POST --data-binary @- http://localhost:8080/requirements.txt | python -m json.tool

    or

    curl -X POST --data-binary @/tmp/requirements.txt http://localhost:8080/requirements.txt | python -m json.tool

    """
    return CACHE.cache_requirements_txt(bottle.request.body)
