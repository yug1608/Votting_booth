from flask import Flask, request, redirect, url_for, render_template_string
import csv, os

app = Flask(__name__)

# ===============================
# === CONFIGURATION ============
# ===============================

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "1234"
CSV_FILE = "voting_results.csv"

CATEGORIES = {
    "Head Boy": ["Aarav Sharma", "Rohan Mehta", "Arjun Patel"],
    "Head Girl": ["Ananya Singh", "Diya Kapoor", "Ishita Verma"],
    "Cultural Head Boy": ["Dev Sharma", "Raj Khanna", "Neel Patel"],
    "Cultural Head Girl": ["Simran Kaur", "Priya Mehta", "Tanya Singh"]
}

# ===============================
# === HTML BASE TEMPLATE =======
# ===============================

base_html = """
<!DOCTYPE html>
<html>
<head>
    <title>Student Council Voting App</title>
    {% raw %}
    <style>
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(to bottom right, #007bff, #00c6ff);
            color: white;
            text-align: center;
            margin: 0;
            padding: 0;
        }
        .container {
            width: 80%;
            margin: auto;
            background: rgba(0, 0, 0, 0.6);
            border-radius: 15px;
            padding: 20px;
            margin-top: 50px;
        }
        button {
            background: #00c6ff;
            border: none;
            padding: 10px 20px;
            margin: 10px;
            border-radius: 10px;
            cursor: pointer;
            color: white;
            font-size: 16px;
        }
        button:hover {
            background: #007bff;
        }
        footer {
            margin-top: 30px;
            font-size: 14px;
            color: #ddd;
        }
    </style>
    {% endraw %}
</head>
<body>
    <div class="container">
        {{ content|safe }}
        <footer>by YUG SINGH</footer>
    </div>
</body>
</html>
"""

# ===============================
# === HOME PAGE ================
# ===============================

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        name = request.form["name"].strip()
        grno = request.form["grno"].strip()
        return redirect(url_for("vote", name=name, grno=grno))

    content = """
    <h2>Welcome to Student Council Voting!</h2>
    <form method="POST">
        <label>Your Name:</label><br>
        <input type="text" name="name" required><br>
        <label>Your GR No.:</label><br>
        <input type="text" name="grno" required><br>
        <button type="submit">Start Voting</button>
    </form>
    <a href="/admin">Admin Login</a>
    """
    return render_template_string(base_html, content=content)


# ===============================
# === VOTING PAGE ==============
# ===============================

@app.route("/vote", methods=["GET", "POST"])
def vote():
    name = request.args.get("name")
    grno = request.args.get("grno")

    if request.method == "POST":
        votes = {"Name": name, "GR No": grno}
        for category in CATEGORIES.keys():
            votes[category] = request.form.get(category, "None")

        file_exists = os.path.isfile(CSV_FILE)
        with open(CSV_FILE, "a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["Name", "GR No"] + list(CATEGORIES.keys()))
            if not file_exists:
                writer.writeheader()
            writer.writerow(votes)

        return redirect(url_for("thank_you"))

    content = "<h2>Vote for Your Candidates</h2><form method='POST'>"
    for position, candidates in CATEGORIES.items():
        content += f"<h3>{position}</h3>"
        for c in candidates:
            content += f"<label><input type='radio' name='{position}' value='{c}' required> {c}</label><br>"
    content += "<button type='submit'>Submit Vote</button></form>"
    return render_template_string(base_html, content=content)


# ===============================
# === THANK YOU PAGE ===========
# ===============================

@app.route("/thank_you")
def thank_you():
    content = """
    <h2>Your vote has been recorded!</h2>
    <form action="/">
        <button type="submit">Back to Home</button>
    </form>
    """
    return render_template_string(base_html, content=content)


# ===============================
# === ADMIN PANEL ==============
# ===============================

@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            return redirect(url_for("admin_panel"))

    content = """
    <h2>Admin Login</h2>
    <form method="POST">
        <input type="text" name="username" placeholder="Username" required><br>
        <input type="password" name="password" placeholder="Password" required><br>
        <button type="submit">Login</button>
    </form>
    <a href="/">Back to Home</a>
    """
    return render_template_string(base_html, content=content)


@app.route("/admin_panel")
def admin_panel():
    results = ""
    if os.path.exists(CSV_FILE):
        with open(CSV_FILE) as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            if rows:
                results += "<table border='1' style='margin:auto;background:white;color:black;'>"
                results += "<tr>" + "".join([f"<th>{h}</th>" for h in reader.fieldnames]) + "</tr>"
                for r in rows:
                    results += "<tr>" + "".join([f"<td>{r[h]}</td>" for h in reader.fieldnames]) + "</tr>"
                results += "</table>"
            else:
                results = "<p>No votes yet.</p>"
    else:
        results = "<p>No votes yet.</p>"

    content = f"""
    <h2>Admin Panel</h2>
    {results}
    <form action="/reset_votes" method="POST">
        <button type="submit">Reset All Votes</button>
    </form>
    <a href="/">Back to Home</a>
    """
    return render_template_string(base_html, content=content)


@app.route("/reset_votes", methods=["POST"])
def reset_votes():
    if os.path.exists(CSV_FILE):
        os.remove(CSV_FILE)
    return redirect(url_for("admin_panel"))


# ===============================
# === RUN SERVER ===============
# ===============================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
