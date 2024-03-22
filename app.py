from api import app
from config import Config
from api.handlers import auth, note, user



if __name__ == '__main__':
    app.run(debug=Config.DEBUG, port=Config.PORT)
