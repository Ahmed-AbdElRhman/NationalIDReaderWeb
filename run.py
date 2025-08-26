
from app import create_app
from app.config import config 
from app.Routes.IDReaderEndPoints import IDReaderEndPoints   


app = create_app(config['development'])
app.register_blueprint(IDReaderEndPoints)


if __name__ == '__main__':
    app.run()
