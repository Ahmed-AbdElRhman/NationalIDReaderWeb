
from app import create_app
from app.config import config 
from app.Services.IDReaderEndService import IDReaderEndService
app = create_app(config['development'])
IDReaderEndService(app)

from app.Routes.IDReaderEndPoints import IDReaderEndPoints   
app.register_blueprint(IDReaderEndPoints)
# Initialize the IDReaderEndService
if __name__ == '__main__':
    app.run()
