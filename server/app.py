#!/usr/bin/env python3

from flask import Flask, request, jsonify, make_response
from flask_migrate import Migrate
from flask_restful import Api, Resource
from models import db, Hero, Power, HeroPower
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

@app.route('/')
def index():
    return '<h1>Code challenge</h1>'

# GET /heroes
@app.route('/heroes', methods=['GET'])
def get_heroes():
    heroes = Hero.query.all()
    return jsonify([hero.to_dict() for hero in heroes])

@app.route('/heroes/<int:id>', methods=['GET'])
def get_hero(id):
    hero = Hero.query.get(id)
    if hero:
        hero_powers = HeroPower.query.filter_by(hero_id=id).all()
        return jsonify({
            'id': hero.id,
            'name': hero.name,
            'super_name': hero.super_name,
            'hero_powers': [hp.to_dict() for hp in hero_powers]
        })
    return jsonify({"error": "Hero not found"}), 404


# GET /powers
@app.route('/powers', methods=['GET'])
def get_powers():
    powers = Power.query.all()
    return jsonify([power.to_dict() for power in powers])

# GET /powers/:id
@app.route('/powers/<int:id>', methods=['GET'])
def get_power(id):
    power = Power.query.get(id)
    if power:
        return jsonify(power.to_dict())
    return jsonify({"error": "Power not found"}), 404

# PATCH /powers/:id
@app.route('/powers/<int:id>', methods=['PATCH'])
def update_power(id):
    data = request.get_json()
    power = Power.query.get(id)
    if power:
        if 'description' in data:
            try:
                power.description = data['description']
                db.session.commit()
                return jsonify(power.to_dict())
            except ValueError as e:
                return jsonify({"errors": ["validation errors"]}), 400
    return jsonify({"error": "Power not found"}), 404



# POST /hero_powers
@app.route('/hero_powers', methods=['POST'])
def create_hero_power():
    data = request.get_json()
    try:
        hero_power = HeroPower(
            hero_id=data['hero_id'],
            power_id=data['power_id'],
            strength=data['strength']
        )
        db.session.add(hero_power)
        db.session.commit()
        return jsonify(hero_power.to_dict())
    except ValueError as e:
        return jsonify({"errors": ["validation errors"]}), 400



if __name__ == '__main__':
    app.run(port=5555, debug=True)
