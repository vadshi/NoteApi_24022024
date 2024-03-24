from config import Config
from flask import Flask, request, abort
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_marshmallow import Marshmallow
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth, MultiAuth
from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from flask_apispec import FlaskApiSpec

security_definitions = {
   "basicAuth": {
       "type": "basic"
   }
}


app = Flask(__name__)
app.config.from_object(Config)
app.config.update({
   'APISPEC_SPEC': APISpec(
        title='Notes Project',
        version='1.0',
        plugins=[MarshmallowPlugin()],
        openapi_version='2.0',
        securityDefinitions=security_definitions,
        security=[],
   ),
   'APISPEC_SWAGGER_URL': '/swagger', # URI API Doc JSON
   'APISPEC_SWAGGER_UI_URL': '/swagger-ui'# URI UI of API Doc
})


db = SQLAlchemy(app)
migrate = Migrate(app, db)
ma = Marshmallow(app)
basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth('Bearer')
multi_auth = MultiAuth(basic_auth, token_auth)
docs = FlaskApiSpec(app)


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
