from flask import Blueprint, render_template
from app.Routes.API_Managers.IDReaderAPI_Mngr import IDReaderAPI_Mngr
from app.utils.logger import get_logger
logger = get_logger(__name__)
# Create a blueprint for IDReader endpoints
IDReaderEndPoints = Blueprint('IDReaderEndPoints', __name__)

#-------- OCR Endpoints --------
@IDReaderEndPoints.route("/")
def index():
    return render_template("index.html")

@IDReaderEndPoints.route("/scann", methods=["GET"])
def scann():
    return render_template("/Scanner/index.html")

@IDReaderEndPoints.route("/process", methods=["POST"])
def process():
    return IDReaderAPI_Mngr.process()

#-------- User Endpoints --------
@IDReaderEndPoints.route("/admin")
def admin():
    logger.debug("Rendering admin page")
    return render_template("admin.html")

@IDReaderEndPoints.route("/login", methods=["POST"])
def login():
    logger.debug("Login User")
    return IDReaderAPI_Mngr.login()

@IDReaderEndPoints.route("/logout", methods=["GET"])
def logout():
    logger.debug("Logging out user")
    return IDReaderAPI_Mngr.logout()

@IDReaderEndPoints.route("/admin/subscription")
def get_subscription_status():
    logger.debug("Fetching subscription status")
    return IDReaderAPI_Mngr.get_subscription_status()

@IDReaderEndPoints.route("/admin/renewsubscription")
def get_subscription_status():
    logger.debug("ReNew the Subscription")
    return IDReaderAPI_Mngr.reNew_Subscriptiobn()
