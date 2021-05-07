from flask import Flask, jsonify
from flask_pymongo import PyMongo
import requests
import random
import json
from datetime import datetime, timedelta
from bson.objectid import ObjectId


app = Flask(__name__)
app.config['MONGO_URI'] = "mongodb://mongo-arbiter:27017/proxiesdb"

mongo = PyMongo(app)


@app.route('/proxies/all')
def get_all_proxies():
    proxies = mongo.db.proxies
    proxies_collection = proxies.find({})
    result = []

    for proxy in proxies_collection:
        proxy["_id"] = str(proxy["_id"])
        result.append(proxy)
    return jsonify(result)


@app.route('/proxies/download')
def download_proxies():
    url_api = "http://pubproxy.com/api/proxy?limit=5&level=anonymous&type=http&https=true&speed=30"
    res = requests.get(url_api)
    status_code = res.status_code
    proxies = mongo.db.proxies
    if status_code == 200:
        list_json = res.json()['data']
        result = []
        for ele in list_json:
            ip_port = ele['ipPort']
            if proxies.count_documents({'ipPort': ip_port}) > 0:
                doc = proxies.find_one_and_update(
                    {'ipPort': ip_port},
                    {"$set":
                        {"last_checked": datetime.strptime(ele['last_checked'], "%Y-%m-%d %H:%M:%S").isoformat()}
                    },upsert=True
                )
            else:
                ele['used'] = False
                ele['last_checked'] = datetime.strptime(ele['last_checked'], "%Y-%m-%d %H:%M:%S").isoformat()
                doc = proxies.insert_one(ele)
            # guardo el proxy obtenido para retornarlo al cliente.
            proxy = proxies.find_one({'ipPort': ip_port})
            proxy["_id"] = str(proxy["_id"])
            result.append(proxy)

        return jsonify(result)

    else:
        return jsonify({
            "error": status_code,
        })


@app.route('/proxies/get')
def get_proxy():
    proxies = mongo.db.proxies
    # Cuento si quedan proxies que no estén siendo usados por algún servicio.
    proxies_count = proxies.count_documents({
        'used': False
    })
    # Si no quedan proxies sin haber sido usado, volvemos a setear el usado en false.
    if proxies_count == 0:
        updated_collection = proxies.update_many({},
            {
                "$set": {
                    "used": False
                }
            }
        )
    # Se pide un proxy disponible
    proxy = {}
    proxy_doc = proxies.find_one({
        'used': False
    })
    proxy_server = proxy_doc['ipPort']
    proxy = {
        "http": proxy_server,
        "https": proxy_server,
    }
    proxy_doc['used'] = True
    # Se actualiza el proxy para indicar que está siendo usado / fue usado.
    query = {'ipPort': proxy_server}
    updated_doc = proxies.update_one(query, {
                "$set": {
                    "used": True
                }
            }
        )

    return jsonify(proxy)


@app.route('/proxies/checked/<int:days>/days', methods=['GET'])
def get_oldest_proxies(days):
    proxies = mongo.db.proxies

    today = datetime.today()
    interval = today - timedelta(days=days)

    proxies_collection = proxies.find(
        {
            'last_checked': 
                {
                    "$lt" : interval.isoformat()
                }
        }
    )

    result = []
    for proxy in proxies_collection:
        proxy["_id"] = str(proxy["_id"])
        result.append(proxy)

    return jsonify(result)

@app.route('/proxies/delete/<id>', methods=['GET'])
def delete_proxy(id):
    proxies = mongo.db.proxies

    proxy_doc = proxies.find_one_and_delete(
        {'_id': ObjectId(id)}
    )

    if proxy_doc:
        proxy_doc['_id'] = str(proxy_doc['_id'])
    else:
        proxy_doc = {}

    return jsonify(proxy_doc)

