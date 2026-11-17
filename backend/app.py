from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
from datetime import datetime

app = Flask(__name__)
CORS(app)
DB = "shiba.db"
MODULES = ["purchase","kitchen","sales","inventory","expenses","staffmeal","production"]

def init_db():
    conn = sqlite3.connect(DB)
    for m in MODULES:
        conn.execute(f"""CREATE TABLE IF NOT EXISTS {m} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT, item TEXT, quantity REAL, amount REAL,
            category TEXT, notes TEXT, created_at TEXT
        )""")
    conn.commit()
    conn.close()

init_db()

@app.route("/api/<module>", methods=["GET","POST"])
def handle_module(module):
    if module not in MODULES and module != "summary":
        return jsonify({"error":"invalid"}),400
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    if request.method == "GET":
        if module == "summary":
            data={}
            for m in MODULES:
                cur.execute(f"SELECT SUM(amount) as total, COUNT(*) as count FROM {m}")
                data[m]=dict(cur.fetchone())
            conn.close()
            return jsonify(data)
        cur.execute(f"SELECT * FROM {module} ORDER BY id DESC")
        rows=[dict(r) for r in cur.fetchall()]
        conn.close()
        return jsonify(rows)
    d=request.json
    cur.execute(f"INSERT INTO {module} (date,item,quantity,amount,category,notes,created_at) VALUES (?,?,?,?,?,?,?)",
                (d.get('date'),d.get('item'),d.get('quantity'),d.get('amount'),d.get('category'),d.get('notes'),datetime.now().isoformat()))
    conn.commit()
    conn.close()
    return jsonify({"status":"added"})

@app.route("/api/<module>/<int:id>", methods=["PUT","DELETE"])
def modify(module,id):
    conn=sqlite3.connect(DB)
    cur=conn.cursor()
    if request.method=="DELETE":
        cur.execute(f"DELETE FROM {module} WHERE id=?",(id,))
    else:
        d=request.json
        cur.execute(f"UPDATE {module} SET date=?,item=?,quantity=?,amount=?,category=?,notes=? WHERE id=?",
                    (d.get('date'),d.get('item'),d.get('quantity'),d.get('amount'),d.get('category'),d.get('notes'),id))
    conn.commit()
    conn.close()
    return jsonify({"status":"ok"})

@app.route("/")
def home():
    return jsonify({"message":"Shiba System API Running","modules":MODULES})

if __name__=="__main__":
    app.run(debug=True, port=5000)
