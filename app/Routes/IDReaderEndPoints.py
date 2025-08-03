from flask import Blueprint, render_template
from app.utils.logger import get_logger
logger = get_logger(__name__)

# Create a blueprint for IDReader endpoints
IDReaderEndPoints = Blueprint('IDReaderEndPoints', __name__)
@IDReaderEndPoints.route("/")
def index():
    #  if not file:
    #         return jsonify({"error": "No file uploaded"}), 400
    return render_template("index.html")
