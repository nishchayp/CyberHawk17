from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
import os

app = Flask(__name__)
app.secret_key = "9999"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "app.sqlite")
db = SQLAlchemy(app)

# flask-login config
login_manager = LoginManager()
login_manager.init_app(app)

class UserCredentials(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userEmail = db.Column(db.String(120), unique=True, nullable=False)
    userName = db.Column(db.String(64), unique=True)
    userPassword = db.Column(db.String(120), nullable=False)

    def __init__(self, userEmail, userName, userPassword):
        self.userEmail = userEmail
        self.userName = userName
        self.userPassword = userPassword

class UserDetails(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userName = db.Column(db.String(64))
    userPhone = db.Column(db.String(20))
    userCollege = db.Column(db.String(120))
    userLevel = db.Column(db.Integer)

    def __init__(self, id, userName, userPhone, userCollege, userLevel):
        self.id = id
        self.userName = userName
        self.userPhone = userPhone
        self.userCollege = userCollege
        self.userLevel = userLevel

db.create_all()
db.session.commit()

# user_loader callback
@login_manager.user_loader
def user_loader(id):
	return UserCredentials.query.get(id)

@app.route("/")
def home():
	return "CyberHawk"

# Route to register new player
@app.route("/addPlayer", methods = ["POST"])
def addPlayer():
	data = request.get_json()
	playerCredentials = UserCredentials(data["userEmail"], data["userName"], data["userPassword"])
	
	# Check if email and username entered are unique
	if db.session.query(UserCredentials.userEmail).filter(UserCredentials.userEmail == playerCredentials.userEmail).count() > 0:
		response = {
			"success": False,
			"data": "Email already registered, try logging in"
		}

	elif db.session.query(UserCredentials.userName).filter(UserCredentials.userName == playerCredentials.userName).count() > 0:
		response = {
			"success": False,
			"data": "Username is taken, try another Username"
		}

	# Register player
	else:
		db.session.add(playerCredentials)
		db.session.commit()

		# Add player details to UserDetails db
		playerDetails = UserDetails(playerCredentials.id, playerCredentials.userName, data["userPhone"], data["userCollege"], 1)
		db.session.add(playerDetails)
		db.session.commit()

		response = {
			"success": True,
			"data": "NULL"
		}

	return jsonify(response)

# Route to login
@app.route("/login", methods = ["POST"])
def login():
	data = request.get_json()

	# Verify username and password
	if db.session.query(UserCredentials.userName).filter(UserCredentials.userName == data["userName"]).count() > 0:
		player = db.session.query(UserCredentials).filter(UserCredentials.userName == data["userName"]).first()
		if (player.userPassword == data["userPassword"]):
			login_user(player, remember=True)
			response = {
				"success": True,
				"data": {
					"id": player.id
				}
			}

		else:
			response = {
				"success": False,
				"error": "incorrect password"
			}

	else:
		response = {
			"success": False,
			"error": "invalid username"
		}
	
	return jsonify(response)

# Route to logout
@app.route("/logout")
@login_required
def logout():
	logout_user()
	response = {
		"success": True,
		"data": "NULL"
	}
	return jsonify(response)

if __name__ == "__main__":
	app.run(debug = True)