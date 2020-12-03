from flask import Flask
from flask_migrate import Migrate
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

from project4.config import Config
from project4.models import db, User, Meal, Order, Category


app = Flask(__name__)
admin = Admin(app)
app.config.from_object(Config)
db.init_app(app)
migrate = Migrate(app, db)

admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Order, db.session))
admin.add_view(ModelView(Meal, db.session))
admin.add_view(ModelView(Category, db.session))

from project4.views import *

if __name__ == "__main__":
    app.run()
