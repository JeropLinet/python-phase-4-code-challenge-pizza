#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response,jsonify
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

@app.route('/restaurants',methods=['GET'])
def get_restaurant():
    restaurants=Restaurant.query.all()
    print("Restaurants found:",restaurants)
  
    restaurants_list=[]
    for restaurant in restaurants:
        restaurant_dict={
          "address":restaurant.address,
          "id":restaurant.id,
          "name":restaurant.name 
        }
        restaurants_list.append(restaurant_dict)
    status=200
    return make_response(jsonify(restaurants_list),status)

@app.route('/restaurants/<int:id>')
def get_restaurant_by_id(id):
    restaurant=RestaurantPizza.query.get(id)
    if restaurant is None:
        response_body={'error':'Restaurant not found'}
        status=404

    restaurant_pizzas=RestaurantPizza.query.filter_by(restaurant_id=id).all()
    pizzas_list=[]

    for rpizza in restaurant_pizzas:
        pizza=Pizza.query.get(rpizza.pizza_id)
        pizza_data={
            "id":pizza.id,
            "ingredients":pizza.ingredients,
            "name":pizza.name
        }
        rpizza_data={
            "id":rpizza.id,
            "pizza":pizza_data,
            "pizza_id":rpizza.pizza_id,
            "price":rpizza.price,
            "restaurant_id":rpizza.restaurant_id
        }
        pizzas_list.append(rpizza_data)

    response_body={
     "address":restaurant.address,
     "id":restaurant.id,
     "name":restaurant.name,
     "restaurant_pizzas":pizzas_list
     }
    status=200
    return make_response(jsonify(response_body),status)

@app.route('/restaurants/<int:id>',methods=['GET','DELETE'])
def delete_restaurant(id):
    restaurant=Restaurant.query.filter(Restaurant.id == id).first()
    if restaurant is None:
        response_body={"error":"Restaurant not found"}
        status=404
        return make_response(jsonify(response_body),status)
    if request.method == 'GET':
        restaurant_dict=restaurant.to_dict()
        return make_response(jsonify(restaurant_dict))
    elif request.method == 'DELETE':
        db.session.delete(restaurant)
        db.session.commit()
        response_body={"message":"Restaurant deleted"}
        status=200
        return make_response(jsonify(response_body),status)

@app.route('/pizzas') 
def get_pizzas():
    pizzas=Pizza.query.all()
    print("Pizzas found:",pizzas)
    if not pizzas:
        return jsonify({"message":"No pizzas found"}),404
    pizzas_list=[]
    for pizza in pizzas:
        pizza_dict={
        "id":pizza.id,
        "ingredients":pizza.ingredients,
        "name":pizza.name
        }
        pizzas_list.append(pizza_dict)
    status=200
    return make_response(jsonify(pizzas_list),status)

@app.route('/restaurant_pizzas',methods=['POST'])
def handle_rpizza():
    new_rpizza=RestaurantPizza(
        price=request.form.get("price"),
        pizza_id=request.form.get("pizza_id"),
        restaurant_id=request.form.get("restaurant_id"),
    )
    pizza=Pizza.query.get(new_rpizza.pizza_id)
    restaurant=Restaurant.query.get(new_rpizza.restaurant_id)

    if not pizza or restaurant:
        response_body={
            "errors":"Sorry Pizza or Restaurant not found"
        }
        status=404
        return make_response(jsonify(response_body),status)
    db.session.add(new_rpizza)
    db.session.commit()

    response_body={
        "id":new_rpizza.id,
        "pizza":{
              "id":pizza.id,
              "ingredients":pizza.ingredients,
              "name":pizza.name
            },
        "pizza_id":new_rpizza.pizza_id,
        "price":new_rpizza.price,
        "restaurant":{
            "address":restaurant.address,
            "id":restaurant.id,
            "name":restaurant.name
            },
        "restaurant_id":new_rpizza.restaurant_id
    }
    status=200
    return make_response(jsonify(response_body),status)
    
if __name__ == "__main__":
    app.run(port=5555, debug=True)
