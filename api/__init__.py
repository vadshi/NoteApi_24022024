from config import Config
from flask import Flask, request, abort
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_marshmallow import Marshmallow
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth, MultiAuth
from flasgger import Swagger


app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
migrate = Migrate(app, db)
ma = Marshmallow(app)
basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth('Bearer')
multi_auth = MultiAuth(basic_auth, token_auth)
swagger = Swagger(app)


@app.errorhandler(404)
def not_found(e):
    response = {'status': 404, 'error': e.description}
    return response, 404


@basic_auth.verify_password
def verify_password(username, password):
    from api.models.user import UserModel
    user_db = UserModel.query.filter_by(username=username).first()
    if not user_db or not user_db.verify_password(password):
        return False
    return user_db


@token_auth.verify_token
def verify_token(token):
    from api.models.user import UserModel
    user_db = UserModel.verify_auth_token(token)
    return user_db


@basic_auth.get_user_roles
def get_user_roles(user):
    return user.get_roles()


@token_auth.get_user_roles
def get_user_roles(user):
    return user.get_roles()


from api.handlers import auth  # noqa: E402, F401
from api.handlers import note  # noqa: E402, F401
from api.handlers import user  # noqa: E402, F401
