from api import app, request, multi_auth
from api.models.user import UserModel
from api.schemas.user import UserRequestSchema, UserSchema, user_schema, users_schema
from flask_apispec import doc, marshal_with, use_kwargs
from flask_babel import _


@app.route("/users/<int:user_id>")
@doc(description='Api for only user.', tags=['Users'], summary="Get user by id")
@marshal_with(UserSchema, code=200)
def get_user_by_id(user_id):
    user = UserModel.query.get_or_404(user_id, f"User with id={user_id} not found")
    return user, 200


@app.route("/users")
@doc(description='Api for all users.', tags=['Users'], summary="Get all users")
@marshal_with(UserSchema(many=True), code=200)
def get_users():
    """
    Get all Users
    ---
    tags:
        - Users
    """
    return UserModel.query.all()


@app.route("/users", methods=["POST"])
@doc(description='Api for create user.', tags=['Users'], summary="Create user")
@use_kwargs(UserRequestSchema, location='json')
@marshal_with(UserSchema, code=201)
def create_user(**kwargs):
    # user_data = request.json
    user = UserModel(**kwargs)
    # DONE: добавить обработчик на создание пользователя с неуникальным username
    if UserModel.query.filter_by(username=user.username).one_or_none():
        return {"error": "User already exists."}, 409
    user.save()
    return user, 201


@app.route("/users/<int:user_id>", methods=["PUT"])
@doc(description='Api for edit user.', tags=['Users'], summary="Edit user")
@doc(responses={"403": {"description": "Unauthorized"}})
@doc(responses={"404": {"description": "Not found"}})
@doc(security= [{"basicAuth": []}])
@use_kwargs(UserRequestSchema, location='json')
@marshal_with(UserSchema, code=200)
@multi_auth.login_required(role="admin")
def edit_user(user_id, **kwargs):
    user = UserModel.query.get_or_404(user_id, f"User with id={user_id} not found")
    for key, value in kwargs.items():
        setattr(user, key, value)
    user.save()
    return user, 200


@app.route("/users/<int:user_id>", methods=["DELETE"])
@doc(description='Api for delete user.', tags=['Users'], summary="Delete user by id")
@doc(responses={"404": {"description": "Not found"}})
@multi_auth.login_required(role="admin")
def delete_user(user_id):
    """
    Пользователь может удалять ТОЛЬКО свои заметки
    1. Найти пользователя по user_id
    2. Вызвать метод delete()
    """
    user = UserModel.query.get_or_404(user_id)
    user.delete()
    return {"message": _("User with id=%(user_id)s has deleted.", user_id=user_id)}

