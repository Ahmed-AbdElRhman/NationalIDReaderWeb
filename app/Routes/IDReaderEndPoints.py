from flask import Blueprint, render_template
from app.Routes.API_Managers.IDReaderAPI_Mngr import IDReaderAPI_Mngr
# Create a blueprint for IDReader endpoints
IDReaderEndPoints = Blueprint('IDReaderEndPoints', __name__)
@IDReaderEndPoints.route("/")
def index():
    return render_template("index.html")
    #  if not file:
    #         return jsonify({"error": "No file uploaded"}), 400

@IDReaderEndPoints.route("/process", methods=["POST"])
def process():
    return IDReaderAPI_Mngr.process()