from flask import Blueprint, render_template
from app.Routes.API_Managers.IDReaderAPI_Mngr import IDReaderAPI_Mngr
from app.utils.logger import get_logger
logger = get_logger(__name__)
# Create a blueprint for IDReader endpoints
IDReaderEndPoints = Blueprint('IDReaderEndPoints', __name__)
@IDReaderEndPoints.route("/")
def index():
    return render_template("index.html")
    #  if not file:
    #         return jsonify({"error": "No file uploaded"}), 400

@IDReaderEndPoints.route("/process", methods=["POST"])
def process():
    try:
        # Call the process method from IDReaderAPI_Mngr
        return IDReaderAPI_Mngr.process()
    except Exception as e:
        # Handle exceptions and return an error response
        logger.error(f"Error in process EndPoint: {str(e)}", exc_info=True)
        return {"Error while process the ID image": str(e)}, 500
