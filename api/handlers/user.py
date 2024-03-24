from api import app, request, multi_auth
from api.models.user import UserModel
from api.schemas.user import UserRequestSchema, UserSchema, user_schema, users_schema
from flask_apispec import doc, marshal_with, use_kwargs


@app.route("/users/<int:user_id>")
@doc(description='Api for only user.', tags=['Users'], summary="Get user by id")
@marshal_with(UserSchema, code=200)
def get_user_by_id(user_id):
    user = UserModel.query.get_or_404(user_id, f"User with id={user_id} not found")
    return user, 200


@app.route("/users")
@doc(description='Api for all users.', tags=['Users'], summary="Get all users")
def get_users():
    """
    Get all Users
    ---
    tags:
        - Users
    """
    users = UserModel.query.all()
    return users_schema.dump(users), 200


@app.route("/users", methods=["POST"])
@doc(description='Api for create user.', tags=['Users'], summary="Create user")
@use_kwargs(UserRequestSchema, location='json')
def create_user(**kwargs):
    # user_data = request.json
    user = UserModel(**kwargs)
    # DONE: добавить обработчик на создание пользователя с неуникальным username
    if UserModel.query.filter_by(username=user.username).one_or_none():
        return {"error": "User already exists."}, 409
    user.save()
    return user_schema.dump(user), 201


@app.route("/users/<int:user_id>", methods=["PUT"])
@doc(description='Api for users.', tags=['Users'])
@multi_auth.login_required(role="admin")
def edit_user(user_id):
    user_data = request.json
    user = UserModel.query.get_or_404(user_id, f"User with id={user_id} not found")
    user.username = user_data["username"]
    user.save()
    return user_schema.dump(user), 200


@app.route("/users/<int:user_id>", methods=["DELETE"])
@doc(description='Api for delete user.', tags=['Users'], summary="Delete user by id")
@multi_auth.login_required(role="admin")
def delete_user(user_id):
    """
    Пользователь может удалять ТОЛЬКО свои заметки
    1. Найти пользователя по user_id
    2. Вызвать метод delete()
    """
    user = UserModel.query.get_or_404(user_id)
    user.delete()
    return {"message": f"User with id={user_id} has deleted."}

