from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)

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

