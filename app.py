from flask import Flask,session, redirect, url_for, request, render_template
from flask import Flask, render_template, abort
from flask import flash
from flask_session import Session
from datetime import datetime,timedelta
from werkzeug.security import  generate_password_hash,check_password_hash
import locale
import os
import pandas as pd

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = True
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
locale.setlocale(locale.LC_TIME, 'es_ES')
#estructura de datos secuencial:lista de diccionarios
books = [
    {"id": 1, "title": "La Chica del tren", "author": "Emily Blunt", "url": "https://sallebello.edu.co/images/La_chica_del_tren_-_Paula_Hawkins.pdf"},
    {"id": 2, "title": "Lo que no te mata", "author": "David Lagercrantz", "url": "https://www.planetadelibros.com.mx/libros_contenido_extra/31/30954_1_Cap1_M4.pdf"},
    {"id": 3, "title": "Orgullo y prejuicio", "author": "Keira Knightley", "url": "https://web.seducoahuila.gob.mx/biblioweb/upload/orgullo_y_prejuicio.pdf"},
    {"id": 4, "title": "Corazon", "author": "Edmondo De Amicis", "url": "https://www.suneo.mx/literatura/subidas/Edmundo%20de%20Amicis%20Coraz%C3%B3n.pdf"},
    {"id": 5, "title": "Don Enrique el doliente", "author": "Mariano José de Larra", "url": "https://web.seducoahuila.gob.mx/biblioweb/upload/El_Doncel_de_Don_Enrique_el_Doliente%20(1).pdf"},
    {"id": 6, "title": "La edad de la inocencia", "author": "Edith Wharton", "url": "https://web.seducoahuila.gob.mx/biblioweb/upload/la_edad_de_la_inocencia.pdf"},
    {"id": 7, "title": "Sherlock Holmes", "author": "Arthur Conan Doyle", "url": "https://libros.metabiblioteca.org/server/api/core/bitstreams/a19d9afa-b786-4541-94f8-5b4790128826/content"},
    {"id": 8, "title": "El abanico de lady Windermere", "author": "Oscar Wilde", "url": "https://www.suneo.mx/literatura/subidas/Oscar%20Wilde%20El%20Abanico%20de%20Lady%20Windermere.pdf"},
    {"id": 9, "title": "El maravilloso mago de oz", "author": "L.frank Baum", "url": "http://bibliotecadigital.ilce.edu.mx/Colecciones/CuentosMas/ElMaravillosoMagoOz_Baum.pdf"},
    {"id": 10, "title": "Los buscadores de tesoros", "author": "Washington Irving", "url": "https://web.seducoahuila.gob.mx/biblioweb/upload/LOS%20BUSCADORES%20DE%20TRESOROS.pdf"},
    {"id": 11, "title": "El Amante de Lady Chatterley", "author": "D. H. Lawrence", "url": "https://web.seducoahuila.gob.mx/biblioweb/upload/Lawrence,%20D.H.%20-%20El%20Amante%20de%20Lady%20Ch.pdf"},
    {"id": 12, "title": "Los Miserables", "author": "Víctor Hugo", "url": "https://cdn.pruebat.org/recursos/recursos/Los-miserables.pdf"},
    {"id": 13, "title": "El Gran Gatsby", "author": "Francis Scott Fitzgerald", "url": "https://www.imprentanacional.go.cr/editorialdigital/libros/literatura%20universal/el_gran_gatsby_edincr.pdf"},
    {"id": 14, "title": "Piense y Hagase Rico", "author": "Napoleon Hill", "url": "https://www.economicas.unsa.edu.ar/afinan/informacion_general/book/piense_y_hagase_rico.pdf"},
    {"id": 15, "title": "El Arte de la Guerra", "author": "Sun Tzu", "url": "https://web.seducoahuila.gob.mx/biblioweb/upload/El_arte_de_la_guerra-Sun_Tzu.pdf"},
    {"id": 16 ,"title": "El Juego de la Vida y Cómo Jugarlo", "author": "Florence Scovel Shinn", "url": "https://www.institutosylviarealty.com/wp-content/uploads/2013/12/ElJuegoDeLaVidaYComoJugarlo-FlorenceScovelShinn.pdf"},

]
# Cargar usuarios desde Excel
# Función para guardar el DataFrame en un archivo Excel
def save_df_to_excel(df, file_name):
    with pd.ExcelWriter(file_name, engine='openpyxl', mode='w') as writer:
        df.to_excel(writer, index=False)

# Función para cargar los usuarios desde Excel
def cargar_usuarios():
    df = pd.read_excel('usuarios.xlsx')
    return df

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:

        return redirect(url_for('libreria'))

    if request.method == 'POST':
        df = cargar_usuarios()
        username = request.form['username']
        password = request.form['password']

        # Verificar si el usuario ya existe en el DataFrame
        if username in df['username'].values:
            user_data = df[df['username'] == username].iloc[0]
            if check_password_hash(user_data['password'], password):
                session['username'] = username
                return redirect(url_for('libreria'))
            else:
                flash('Contraseña incorrecta.')
                return redirect(url_for('login'))
        else:
            # Si el usuario no existe, registrar nuevo usuario
            new_data = pd.DataFrame({
                'username': [username],
                'password': [generate_password_hash(password)]  # Guardar hash de la contraseña
            })
            df = pd.concat([df, new_data], ignore_index=True)
            df.to_excel('usuarios.xlsx', index=False)  # Guardar en Excel
            session['username'] = username
            session['just_logged_in'] = True  # Establecer la bandera también aquí
            return redirect(url_for('libreria'))

    return render_template('login.html')
#libreria, verifica si el usuario esta logeado y despliega un pop up
@app.route('/')
def libreria():
    if 'username' not in session:
        return redirect(url_for('login'))
    just_logged_in = session.pop('just_logged_in', False)
    return render_template('libreria.html', username=session.get('username'), just_logged_in=just_logged_in)


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/add_to_cart/<int:book_id>', methods=['POST'])
def add_to_cart(book_id):
    if 'cart' not in session:
        session['cart'] = []#lista que almacena los detalles de los libros añadidos al carrito.
        # & diccionario que contiene información sobre un libro específico.
    title = request.form.get('title')
    author = request.form.get('author')
    url = request.form.get('url')
    if book_id not in [b['id'] for b in session['cart']]:
        book = next((b for b in books if b['id'] == book_id), None)
        if book:
            updated_book = {
                'id': book['id'],
                'title': title if title else book['title'],
                'author': author if author else book['author'],
                'url': url if url else book['url'],
                'fecha_prestamo': datetime.now().strftime("%d/%m/%Y"),
                'fecha_vencimiento': (datetime.now() + timedelta(days=30)).strftime("%d/%m/%Y")
            }
            session['cart'].append(updated_book)
            session.modified = True

    return redirect(url_for('prestamos'))

@app.route('/libros/prestamos')
def prestamos():
    cart = session.get('cart', [])
    today = datetime.now()
    vencidos = []

    for item in cart:

        if 'fecha_vencimiento' in item:

            fecha_vencimiento = datetime.strptime(item['fecha_vencimiento'], "%d/%m/%Y")


            if fecha_vencimiento < today:
                vencidos.append(item['title'])
                flash(f'El libro "{item["title"]}" ha vencido el {item["fecha_vencimiento"]}. Por favor, realiza la devolución lo antes posible.', 'error')
        else:

            flash(f'Error: No se encontró fecha de vencimiento para "{item.get("title", "Unknown")}".', 'error')

    return render_template('prestamos.html', cart=cart, vencidos=vencidos, books=books)
    return render_template('usuario.html', book=books)

@app.route('/remove_from_cart/<int:book_id>', methods=['POST'])
def remove_from_cart(book_id):
    print("Cart before removal:", session.get('cart'))
    if 'cart' in session:
        session['cart'] = [book for book in session['cart'] if book['id'] != book_id]
        session.modified = True
    print("Cart after removal:", session.get('cart'))
    return redirect(url_for('prestamos'))

def get_cart_items():
    cart = session.get('cart', [])
    return cart

@app.route('/libros')
def libros():
    return render_template('libros.html', book=books)

@app.route('/libros1')
def libros1():
    return render_template('libros1.html',  book=books)
@app.route('/libros2')
def libros2():
    return render_template('libros2.html', book=books)
@app.route('/libros/romance')
def romance():
    return render_template('romance.html', book=books)
@app.route('/libros/drama')
def drama():
    return render_template('drama.html', book=books)
@app.route('/libros/fantasia')
def fantasia():
    return render_template('fantasia.html', book=books)
@app.route('/usuario')
def usuario():
    cart = get_cart_items()  # Correctamente ubicada dentro de la función
    just_logged_out = session.pop('just_logged_out', False)

    if 'username' in session:
        return render_template('usuario.html', cart=cart, username=session['username'], just_logged_out=just_logged_out)
    else:
        return redirect(url_for('login'))





if __name__=='__main__':
    app.run(debug=True, port=5000)
