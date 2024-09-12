#!/usr/bin/env python3

from flask import Flask, request, jsonify, make_response
from flask_migrate import Migrate
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
    heroes_list = [
        {
            "id": hero.id,
            "name": hero.name,
            "super_name": hero.super_name
        } 
        for hero in heroes
    ]
    return jsonify(heroes_list)

# GET /heroes/<int:id>
@app.route('/heroes/<int:id>', methods=['GET'])
def get_hero(id):
    hero = db.session.get(Hero, id)
    if not hero:
        return jsonify({"error": "Hero not found"}), 404

    hero_powers = HeroPower.query.filter_by(hero_id=id).all()
    hero_powers_data = []

    for hero_power in hero_powers:
        power = db.session.get(Power, hero_power.power_id)
        if power:
            hero_powers_data.append({
                "hero_id": hero_power.hero_id,
                "id": hero_power.id,
                "power_id": hero_power.power_id,
                "strength": hero_power.strength,
                "power": {
                    "id": power.id,
                    "name": power.name,
                    "description": power.description
                }
            })

    response_data = {
        "id": hero.id,
        "name": hero.name,
        "super_name": hero.super_name,
        "hero_powers": hero_powers_data
    }

    return jsonify(response_data)

# GET /powers
@app.route('/powers', methods=['GET'])
def get_powers():
    powers = Power.query.all()
    powers_list = [
        {
            "id": power.id,
            "name": power.name,
            "description": power.description
        } 
        for power in powers
    ]
    return jsonify(powers_list)

# GET /powers/<int:id>
@app.route('/powers/<int:id>', methods=['GET'])
def get_power(id):
    power = db.session.get(Power, id)
    if not power:
        return jsonify({"error": "Power not found"}), 404

    power_data = {
        "id": power.id,
        "name": power.name,
        "description": power.description
    }
    return jsonify(power_data)

@app.route('/powers/<int:id>', methods=['PATCH'])
def update_power(id):
    power = db.session.get(Power, id)
    if not power:
        return jsonify({'error': 'Power not found'}), 404

    data = request.get_json()

    errors = []

    # Validate description
    description = data.get('description')
    if description is not None:
        if len(description) < 20:
            errors.append('Description must be at least 20 characters long')
    
    if errors:
        return jsonify({'errors': ['validation errors']}), 400
    
    if description is not None:
        power.description = description
    
    db.session.commit()

    return jsonify({
        'id': power.id,
        'name': power.name,
        'description': power.description
    })

@app.route('/hero_powers', methods=['POST'])
def create_hero_power():
    data = request.get_json()
    hero_id = data.get('hero_id')
    power_id = data.get('power_id')
    strength = data.get('strength')

    if strength not in ['Strong', 'Weak', 'Average']:
        return jsonify({'errors': ['validation errors']}), 400

    hero = db.session.get(Hero, hero_id)
    power = db.session.get(Power, power_id)

    if not hero or not power:
        return jsonify({'errors': ['Hero or Power not found']}), 404

    new_hero_power = HeroPower(hero_id=hero_id, power_id=power_id, strength=strength)
    db.session.add(new_hero_power)
    db.session.commit()

    return jsonify({
        'id': new_hero_power.id,
        'hero_id': new_hero_power.hero_id,
        'power_id': new_hero_power.power_id,
        'strength': new_hero_power.strength,
        'hero': {'id': hero.id, 'name': hero.name, 'super_name': hero.super_name},
        'power': {'id': power.id, 'name': power.name, 'description': power.description}
    }), 200

if __name__ == '__main__':
    app.run(port=5555, debug=True)
