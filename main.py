import json
from flask import Flask, render_template, url_for, redirect
import requests
from redis_om import get_redis_connection

redis_conn = get_redis_connection()

app = Flask(__name__)

@app.route('/characters')
def all_chars():
    return all_chars_pags(1)

@app.route('/characters/<page>')
def all_chars_pags(page):
    tabla = f'characters_pag_{page}'
    a = redis_conn.get(tabla)
    if a:
        print("Existen datos en caché")
        return json.loads(a)
    else:
        print("No existen datos en caché")
        link = f"https://rickandmortyapi.com/api/character/?page={page}"
        x = requests.get(link)
        print(x)
        redis_conn.set(tabla, json.dumps(x.json(), separators=(',', ':')), ex=60)
        return x.json()


@app.route('/character/<id>')
def one_char(id):
    if id==0:
        return all_chars()
    else:
        tabla = f'character_{id}'
        a = redis_conn.get(tabla)
        if a:
            print("Existen datos en caché")
            return render_template('character.html', data=json.loads(a))
            #return json.loads(a)
        else:
            print("No existen datos en caché")
            x = requests.get(f"https://rickandmortyapi.com/api/character/{id}")
            redis_conn.set(tabla, json.dumps(x.json(), separators=(',', ':')))
            return render_template('character.html', data=x.json())
            #return x.json()

@app.route('/<id>')
def del_char(id):
    print("Borrar")
    tabla = f'character_{id}'
    redis_conn.delete(tabla)
    return redirect(url_for('all_chars'))



if __name__ == '__main__':
    app.run(debug=True)