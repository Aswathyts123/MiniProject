import joblib
import pandas as pd

from flask import Flask, render_template, request, redirect, session, url_for, flash
import sqlite3

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Load ML model
model = joblib.load("forest_model.pkl")
forest_encoder=joblib.load("forest_encoder.pkl")
model_columns = joblib.load("forest_model_columns.pkl")



def get_db_connection():
    conn = sqlite3.connect("users.db")
    conn.row_factory = sqlite3.Row
    return conn


# ---------------- Routes ----------------


@app.route("/")
def home():
    return render_template("home.html")

@app.route("/")
def index():
    return render_template("index.html")
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn=sqlite3.connect("users.db") 
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username=?",(username,))
        existing_user=cur.fetchone()
        if existing_user:
             flash("Username already exists.Please choose another")
             conn.close()
             return render_template("register.html")
        else:
             cur.execute("INSERT INTO users (username,password) VALUES(?,?)", (username, password))
             conn.commit()
             conn.close()
             flash("Registration successful ! Please log in..")
             return redirect("/")
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("users.db")
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = cur.fetchone()
        conn.close()

        if user:
            session["user"] = username
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid username or password")
            return render_template("index.html")
    return render_template("index.html")
@app.route("/dashboard")
def dashboard():
    if "user" in session:
        return render_template("dashboard.html", user=session["user"])
    return redirect(url_for("login"))

# ---------------- Prediction Route ----------------
@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Collect raw inputs
        input_data = {
            "Pet_Category": request.form.get("pet_category"),
            "Breed": request.form.get("breed"),
            "Age": int(request.form.get("age")) if request.form.get("age") else 0,
            "Gender": request.form.get("gender"),
            "Weight": float(request.form.get("weight")) if request.form.get("weight") else 0,
            "Symptom1": request.form.get("symptom1"),
            "Symptom2": request.form.get("symptom2"),
            "Symptom3": request.form.get("symptom3"),
            "Duration": request.form.get("duration") 
        }

        # Convert into DataFrame
        input_df = pd.DataFrame([input_data])

        # One-hot encode like training
        input_df = pd.get_dummies(input_df)

        # Reindex to match training columns
        input_df = input_df.reindex(columns=model_columns, fill_value=0)

        # Predict
        prediction = model.predict(input_df)
        predicted_label=prediction[0]
        predicted_disease=forest_encoder.inverse_transform([predicted_label])[0]

        return render_template("result.html",predicted_disease=predicted_disease)

    except Exception as e:
        error_message=f"An error occured:{e}"
        return render_template("result.html",predicted_disease=f"Error:{e}")



if __name__ == "__main__":
    app.run(debug=True)



