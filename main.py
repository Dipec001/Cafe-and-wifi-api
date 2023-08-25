from flask import Flask, jsonify, render_template, request, redirect, url_for, abort
from flask_sqlalchemy import SQLAlchemy
import random
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


##Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        # Method 1.
        dictionary = {}
        # Loop through each column in the data record
        for column in self.__table__.columns:
            # Create a new dictionary entry;
            # where the key is the name of the column
            # and the value is the value of the column
            dictionary[column.name] = getattr(self, column.name)
        return dictionary

        # # Method 2. Altenatively use Dictionary Comprehension to do the same thing.
        # return {column.name: getattr(self, column.name) for column in self.__table__.columns}


@app.route("/")
def home():
    return render_template("index.html")


## HTTP GET - Read Record
@app.route('/random')
def read():
    all_cafes = db.session.query(Cafe).all()
    chosen_cafe = random.choice(all_cafes)

    return jsonify(chosen_cafe.to_dict())


@app.route('/all')
def read_all():
    all_cafes = db.session.query(Cafe).all()
    cafes = []
    for cafe in all_cafes:
        cafes.append(cafe.to_dict())
    return jsonify(cafes)


@app.route('/search')
def search():
    location = request.args.get("loc")
    if location:
        cafes = Cafe.query.filter_by(location=location).all()
        cafes_list = [cafe.to_dict() for cafe in cafes]
        return jsonify(cafes_list)
    else:
        return jsonify(error={"Not Found": "Sorry, we don't have a cafe at that location"})


# HTTP POST - Create Record
@app.route("/add", methods=["POST"])
def post_new_cafe():
    name = request.form.get("name")
    if not name:
        return jsonify(error="Name is required."), 400

    new_cafe = Cafe(
        name=request.form.get("name"),
        map_url=request.form.get("map_url"),
        img_url=request.form.get("img_url"),
        location=request.form.get("loc"),
        has_sockets=bool(request.form.get("sockets")),
        has_toilet=bool(request.form.get("toilet")),
        has_wifi=bool(request.form.get("wifi")),
        can_take_calls=bool(request.form.get("calls")),
        seats=request.form.get("seats"),
        coffee_price=request.form.get("coffee_price"),
    )
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(response={"success": "Successfully added the new cafe."})


# HTTP PUT/PATCH - Update Record
@app.route('/update-price/<cafe_id>', methods=['PATCH'])
def update_price(cafe_id):
    updated_price = request.args.get('coffee_price')

    cafe = Cafe.query.get(cafe_id)
    if cafe:
        cafe.coffee_price = updated_price
        db.session.commit()
        return jsonify(Success='Cafe price updated successfully'), 200
    else:
        # 404 = Resource not found
        return jsonify(error='Cafe not found'), 404


# HTTP DELETE - Delete Record
@app.route('/report-closed/<cafe_id>', methods=['DELETE'])
def delete_cafe(cafe_id):
    api_key = request.args.get('api-key')
    if api_key == 'TopSecretAPIKey':
        cafe = db.session.query(Cafe).get(cafe_id)
        if cafe:
            db.session.delete(cafe)
            db.session.commit()
            return jsonify(response={"success": "Successfully deleted the cafe from the database."}), 200
        else:
            return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."}), 404
    else:
        return jsonify(error={"Forbidden": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403


if __name__ == '__main__':
    app.run(debug=False)
