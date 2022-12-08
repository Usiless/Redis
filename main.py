import json
from flask import Flask, render_template, url_for, redirect, request
import requests
from redis_om import get_redis_connection

redis_conn = get_redis_connection()

app = Flask(__name__)

@app.route('/')
def index():
    return redirect('/characters')


@app.route('/characters')
def all_chars():
    tabla = f'characters'
    a = redis_conn.get(tabla)
    if a:
        print("Existen datos en caché")
        resultados = json.loads(a)
        return render_template('all_characters.html', resultados=resultados)

    else:
        print("No existen datos en caché")
        link = f"https://rickandmortyapi.com/api/character"
        x = requests.get(link)
        y = x.json()
        z = json.dumps(y.get('results'), separators=(',', ':'))
        
        for i in range(2,42):
            link = f"https://rickandmortyapi.com/api/character/?page={i}"
            x = requests.get(link)
            y = x.json()
            aux = json.dumps(y.get('results'), separators=(',', ':'))
            z = z + aux
        z = z.replace('][', ',')
        redis_conn.set(tabla, z , ex=180)
        resultados = json.loads(z)
        return render_template('all_characters.html', resultados=resultados)

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

        else:
            print("No existen datos en caché")
            x = requests.get(f"https://rickandmortyapi.com/api/character/{id}")
            print(type(x))
            redis_conn.set(tabla, json.dumps(x.json(), separators=(',', ':')))
            return render_template('character.html', data=x.json())

@app.route('/delete/<id>')
def del_char(id):
    print("Borrar")
    tabla = f'character_{id}'
    redis_conn.delete(tabla)
    return redirect(url_for('index'))

@app.route('/edit/<id>', methods = ['GET','POST'])
def edit_char(id):
    if request.method=="GET":
        tabla = f'character_{id}'
        a = redis_conn.get(tabla)
        return render_template('character_edit.html', data=json.loads(a))
    elif request.method=="POST":
        especie = request.form['especie']
        genero = request.form['genero']
        origen = request.form['origen']
        lugar = request.form['lugar']
        estado = request.form['estado']
        tabla = f'character_{id}'
        a = redis_conn.get(tabla)
        y = json.loads(a)
        y['status'] = estado
        y['species'] = especie
        y['gender'] = genero
        y['origin']['name'] = origen
        y['location']['name'] = lugar
        redis_conn.delete(tabla)
        redis_conn.set(tabla, json.dumps(y, separators=(',', ':')))
        return render_template('character.html', data=y)


if __name__ == '__main__':
    app.run(debug=True)