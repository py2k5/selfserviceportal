# ssportal/__init__.py
from flask import Flask
from .views.home import home_bp
from .views.zabbix import zabbix
from .views.pingdom import pingdom

app = Flask(__name__)
app.register_blueprint(home_bp)
app.register_blueprint(zabbix)
app.register_blueprint(pingdom)


