from flask import Flask
from flask import Blueprint


app = Flask(__name__)

app.secret_key = 'your secret key'

from worldwaytravel import customer
from worldwaytravel import staff
from worldwaytravel import manager
from worldwaytravel import administrator
from worldwaytravel import visitor
from worldwaytravel import register
from worldwaytravel import login

from .customer import customer
from .staff import staff
from .manager import manager
from .administrator import administrator
from .register import register
from .login import login
from .visitor import visitor

app.register_blueprint(visitor)
app.register_blueprint(customer, url_prefix="/customer")
app.register_blueprint(staff, url_prefix="/staff")
app.register_blueprint(manager, url_prefix="/manager")
app.register_blueprint(administrator, url_prefix="/administrator")
app.register_blueprint(register, url_prefix="/register")
app.register_blueprint(login, url_prefix="/login")