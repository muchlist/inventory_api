from flask import Flask
from flask_jwt_extended import JWTManager
from flask_uploads import configure_uploads, patch_request_class

from config import config as cf
from dao.user_query import get_one_without_password
from databases.db import mongo
from routes.apps_route import bp as apps_bp
from routes.apps_history_route import bp as apps_history_bp
from routes.cctv_route import bp as cctv_bp
from routes.computer_route import bp as computer_bp
from routes.history_route import bp as history_bp
from routes.image_route import bp as image_bp
from routes.option_route import bp as option_bp
from routes.stock_route import bp as stock_bp
from routes.user_route import bp as user_bp
from routes.user_route_admin import bp as user_bp_admin
from utils.image_helper import IMAGE_SET
from utils.my_bcrypt import bcrypt
from utils.my_encoder import JSONEncoder

app = Flask(__name__)

app.config['MONGO_URI'] = cf.get('mongo_uri')
app.config['JWT_SECRET_KEY'] = cf.get('jwt_secret_key')
app.config["UPLOADED_IMAGES_DEST"] = cf.get('uploaded_image_dest')
patch_request_class(app, 6 * 1024 * 1024)  # 6MB max upload.
configure_uploads(app, IMAGE_SET)

mongo.init_app(app)
bcrypt.init_app(app)
jwt = JWTManager(app)

app.json_encoder = JSONEncoder


@jwt.user_claims_loader
def add_claims_to_jwt(identity):
    user = get_one_without_password(identity)
    return {
        "name": user["name"],
        "branch": user["branch"],
        "isAdmin": user["isAdmin"],
        "isEndUser": user["isEndUser"],
    }


app.register_blueprint(user_bp)
app.register_blueprint(user_bp_admin)
app.register_blueprint(history_bp)
app.register_blueprint(computer_bp)
app.register_blueprint(option_bp)
app.register_blueprint(cctv_bp)
app.register_blueprint(stock_bp)
app.register_blueprint(apps_bp)
app.register_blueprint(apps_history_bp)
app.register_blueprint(image_bp)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
