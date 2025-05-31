from flask import Flask, render_template, request,redirect
import pandas as pd
import matplotlib.pyplot as plt
import base64
import seaborn as sns
import io

app = Flask(__name__)

@app.route("/")
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Expense Tracker</title>
        <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
    </head>
    <body>
        <div class="container mt-5">
            <h1 class="mb-4">Welcome to the Expense Tracker</h1>
            <a href="/expense" class="btn btn-primary mr-2">View Expenses</a>
            <a href="/add" class="btn btn-success">Add New Expense</a>
            <a href="/chart" class="btn btn-info">View Spending Chart</a>

        </div>
    </body>
    </html>
    """

from datetime import datetime

@app.route("/chart")
def spending_chart():
    df = pd.read_csv("synthetic_expense_data.csv")
    df["Date"] = pd.to_datetime(df["Date"])
    daily = df.groupby(df["Date"].dt.date)["amount"].sum().reset_index()
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

