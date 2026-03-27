from flask import Flask, render_template, redirect, send_file, request, session
import qrcode
import io

app = Flask(__name__)
app.secret_key = "secret123"   # ✅ REQUIRED for login/session

# 🔐 Users
users = {
    "admin": "1234",
    "user": "1234"
}

token_number = 1
last_token = None

counters = {
    "Counter 1": [],
    "Counter 2": [],
    "Counter 3": [],
    "Counter 4": []
}

now_serving = {
    "Counter 1": None,
    "Counter 2": None,
    "Counter 3": None,
    "Counter 4": None
}

service_time = {
    "Counter 1": 2,
    "Counter 2": 1.5,
    "Counter 3": 2.5,
    "Counter 4": 1.8
}

# 🔐 LOGIN
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip().lower()
        password = request.form["password"].strip()

        if username in users and users[username] == password:
            session["user"] = username
            if username == "admin":
                return redirect("/admin")
            else:
                return redirect("/home")
        else:
            return "Invalid Credentials"

    return render_template("login.html")


# 🏠 HOME
@app.route("/home")
def home():
    if "user" not in session:
        return redirect("/")

    best_counter = min(counters, key=lambda x: len(counters[x]))
    total_people = sum(len(q) for q in counters.values())
    graph_data = [len(q) for q in counters.values()]

    waiting_time = {
        counter: round(len(queue) * service_time[counter] + 1, 2)
        for counter, queue in counters.items()
    }

    return render_template(
        "index.html",
        counters=counters,
        best=best_counter,
        total=total_people,
        graph=graph_data,
        wait=waiting_time,
        serving=now_serving,
        last_token=last_token
    )


# ➕ JOIN
@app.route("/join")
def join():
    if "user" not in session:
        return redirect("/")

    global token_number, last_token

    best_counter = min(counters, key=lambda x: len(counters[x]))
    counters[best_counter].append(token_number)

    last_token = token_number
    token_number += 1

    return redirect("/home")


# ⏭ NEXT
@app.route("/next/<counter>")
def next_customer(counter):
    if "user" not in session:
        return redirect("/")

    if counters[counter]:
        now_serving[counter] = counters[counter].pop(0)

    return redirect("/home")


# 🔄 RESET
@app.route("/reset")
def reset():
    if "user" not in session:
        return redirect("/")

    global counters, token_number, now_serving

    counters = {
        "Counter 1": [],
        "Counter 2": [],
        "Counter 3": [],
        "Counter 4": []
    }

    now_serving = {
        "Counter 1": None,
        "Counter 2": None,
        "Counter 3": None,
        "Counter 4": None
    }

    token_number = 1

    return redirect("/home")


# 👨‍💼 ADMIN
@app.route("/admin")
def admin():
    if "user" not in session:
        return redirect("/")

    return render_template("admin.html", counters=counters, serving=now_serving)


# 📱 MOBILE
@app.route("/mobile")
def mobile():
    return render_template("mobile.html")


# 🔳 QR
@app.route("/qr/<int:token>")
def qr(token):
    img = qrcode.make(f"Token Number: {token}")
    buf = io.BytesIO()
    img.save(buf)
    buf.seek(0)
    return send_file(buf, mimetype='image/png')


# 🚪 LOGOUT
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")


if __name__ == "__main__":
    app.run()