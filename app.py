from flask import Flask, request
from flask_marshmallow import Marshmallow
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy
from marshmallow import ValidationError

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres+psycopg2://postgres:passwd@todo_postgres:5432/postgres'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
ma = Marshmallow(app)
api = Api(app)


##### MODELS #####

class TodoList(db.Model):
    __tablename__ = 'todo_list'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    is_status = db.Column(db.Boolean, index=True)
    created_at = db.Column(db.Date, index=True, nullable=False)
    content = db.Column(db.Text, nullable=True)


##### SCHEMAS #####

def must_not_be_blank(data):
    if not data:
        raise ValidationError("Data not provided.")


class TodoSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = TodoList
        fields = ('id', 'name', 'is_status', 'content', 'created_at')


todo_schema = TodoSchema()
todo_list_schema = TodoSchema(many=True)


##### API #####

class TodoViewSet(Resource):
    def get(self):
        args = request.args
        if args:
            todos_lst = todo_list_schema.dump(TodoList.query.filter_by(is_status=args['status']))
        else:
            todos_lst = todo_list_schema.dump(TodoList.query.all())
        return todos_lst, 200

    def post(self):
        try:
            data = todo_schema.load(request.json)
        except ValidationError as err:
            return err, 401

        todo = TodoList(content=data['content'], name=data['name'], created_at=data['created_at'],
                        is_status=data['is_status'])

        db.session.add(todo)
        db.session.commit()

        output_data = todo_schema.dump(todo)
        return output_data, 201


class TodoListViewSet(Resource):
    def get(self, todo_id):
        todo = TodoList.query.get(todo_id)
        data = todo_schema.dump(todo)
        if data:
            return data, 200
        return "Object not found", 404

    def put(self, todo_id):
        todo = TodoList.query.get(todo_id)
        try:
            data = todo_schema.load(request.json)
        except ValidationError as err:
            print(10 * '------')
            return err, 401

        if todo:
            todo.content = data['content']
            todo.name = data['name']
            todo.is_status = data['is_status']

            db.session.add(todo)
            db.session.commit()

            output_data = todo_schema.dump(todo)
            return output_data, 201
        return "Object not found", 404


api.add_resource(TodoViewSet, '/api/v1/todos')
api.add_resource(TodoListViewSet, '/api/v1/todos/<todo_id>')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)
