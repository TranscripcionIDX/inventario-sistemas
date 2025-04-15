from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import qrcode
import os
import uuid

app = Flask(__name__)
QR_FOLDER = os.path.join("static", "qr_codes")
os.makedirs(QR_FOLDER, exist_ok=True)

def init_db():
    conn = sqlite3.connect("inventario.db")
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS sistemas (
            id TEXT PRIMARY KEY,
            nombre TEXT,
            descripcion TEXT,
            encargado TEXT,
            fecha_apertura TEXT,
            ram TEXT,
            almacenamiento TEXT,
            procesador TEXT,
            so TEXT,
            licencia_windows TEXT,
            licencia_office TEXT,
            quien_entrega TEXT,
            quien_recibe TEXT,
            qr_path TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route("/")
def index():
    conn = sqlite3.connect("inventario.db")
    c = conn.cursor()
    c.execute("SELECT * FROM sistemas")
    sistemas = c.fetchall()
    conn.close()
    return render_template("index.html", sistemas=sistemas)

@app.route("/nuevo", methods=["GET", "POST"])
def nuevo():
    if request.method == "POST":
        data = request.form
        id_unico = str(uuid.uuid4())

        # QR con nombre y ID
        qr_data = f"Equipo: {data['nombre']}, ID: {id_unico}"
        qr_img_path = os.path.join(QR_FOLDER, f"{id_unico}.png")
        img = qrcode.make(qr_data)
        img.save(qr_img_path)

        conn = sqlite3.connect("inventario.db")
        c = conn.cursor()
        c.execute('''
            INSERT INTO sistemas VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            id_unico,
            data["nombre"],
            data["descripcion"],
            data["encargado"],
            data["fecha_apertura"],
            data["ram"],
            data["almacenamiento"],
            data["procesador"],
            data["so"],
            data["licencia_windows"],
            data["licencia_office"],
            data["quien_entrega"],
            data["quien_recibe"],
            qr_img_path
        ))
        conn.commit()
        conn.close()
        return redirect(url_for("index"))
    return render_template("nuevo.html")

if __name__ == "__main__":
    app.run(debug=True)
