from models.orm import Base
from flask_sqlalchemy import SQLAlchemy

# Required for use in Flask. This variable integrates the models the inherits from Base.
db = SQLAlchemy(model_class=Base)