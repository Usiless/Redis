import json
from flask import Flask
import requests
from redis_om import get_redis_connection

redis_conn = get_redis_connection()

app = Flask(__name__)

@app.route('/character')
def all_chars():
    tabla = 'characters'
    a = redis_conn.get(tabla)
    if a:
        print("Existen datos en caché")
        return json.loads(a)
    else:
        print("No existen datos en caché")
        x = requests.get("https://rickandmortyapi.com/api/character")
        redis_conn.set(tabla, json.dumps(x.json(), separators=(',', ':')))
        return x.json()


@app.route('/character/<id>')
def one_chars(id):
    tabla = f'character_{id}'
    a = redis_conn.get(tabla)
    if a:
        print("Existen datos en caché")
        return json.loads(a)
    else:
        print("No existen datos en caché")
        x = requests.get(f"https://rickandmortyapi.com/api/character/{id}")
        redis_conn.set(tabla, json.dumps(x.json(), separators=(',', ':')))
        return x.json()


if __name__ == '__main__':
    app.run(debug=True)