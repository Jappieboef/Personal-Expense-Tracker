from flask import Flask, render_template, request,redirect, url_for, session
import pandas as pd
import matplotlib.pyplot as plt
import base64
import seaborn as sns
import io

app = Flask(__name__)
app.secret_key = 'supersecretkey'


import openai
import os

openai.api_key = os.environ.get("OPENAI_API_KEY")  # or set it directly (not recommended)

@app.route("/analyze", methods=["GET", "POST"])
def analyze_spending():
    import pandas as pd
    import openai

    df = pd.read_csv("synthetic_expense_data.csv")
    
    # Optional filtering
    keyword = request.form.get("filter")
    if keyword:
        df = df[df["Category"].str.contains(keyword, case=False, na=False)]

    summary_text = df.to_string(index=False)[:3000]

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a financial assistant that helps analyze personal expenses."},
            {"role": "user", "content": f"Analyze the following expenses:\n{summary_text}"}
        ]
    )

    analysis = response.choices[0].message["content"]
    return render_template("analysis.html", analysis=analysis)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        requested_username = request.form.get("username")
        requested_password = request.form.get("password")
        
        if requested_username == "admin" and requested_password == "pass123":
            session["user"] = requested_username
            return redirect("/expense")
        else:
            return "Invalid username or password", 401

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")


@app.route("/")
def home():
    return render_template("home.html")


from datetime import datetime

@app.route("/chart")
def spending_chart():
    df = pd.read_csv("synthetic_expense_data.csv")
    df["Date"] = pd.to_datetime(df["Date"])
    daily = df.groupby(df["Date"].dt.date)["Amount"].sum().reset_index()
    plt.figure(figsize=(10, 5))
    sns.lineplot(data=daily, x="Date", y="Amount", marker="o")
    plt.title("Spending Over Time")
    plt.xlabel("Date")
    plt.ylabel("Total Spent")
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Save plot to a memory buffer as PNG
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf8')
    plt.close()

    return render_template("chart_py.html", chart=img_base64)

@app.route("/add", methods=["GET", "POST"])
def add_expense():
    if "user" not in session:
        return redirect("/login")
    else:
        if request.method == "POST":
            date = request.form.get("date")
            category = request.form.get("category")
            description = request.form.get("description")
            amount = request.form.get("amount")

            new_row = [date, category,description, float(amount)]

            filename = "synthetic_expense_data.csv"
            file_exist = os.path.isfile(filename)
            with open(filename, "a") as f:
                if not file_exist:
                    f.write("Date,Category,Amount\n")
                f.write(",".join(map(str, new_row)) + "\n")
            return redirect("/expense")
        return render_template("add.html")

@app.route("/expense", methods=["GET","POST"])
def view_expenses():
    if "user" not in session:
        return redirect("/login")

    try:
        df = pd.read_csv("synthetic_expense_data.csv")

        # get selected category from form
        selected_category = request.form.get("category")

        # create list of categories for dropdown
        all_categories = sorted(df["Category"].unique())
        categories = ["All"] + all_categories

        # filter if category selected
        if selected_category and selected_category != "All":
            df = df[df["Category"] == selected_category]

        # create HTML table and render
        table_html = df.to_html(classes="table table-striped table-bordered", index=False)
        return render_template("expense.html", table=table_html, categories=categories, selected=selected_category or "All")

    except FileNotFoundError:
        return "No expenses recorded yet!"

if __name__ == "__main__":
    import os

port = int(os.environ.get("PORT", 5000))
app.run(host="0.0.0.0", port=port, debug=True)

