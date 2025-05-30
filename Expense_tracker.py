import pandas as pd




df = pd.read_csv('synthetic_expense_data.csv')
print(df.head())
print(df.describe())
# Display the first few rows of the DataFrame
print(df.columns)
food_expenses = df[df['Category'] == 'Groceries']
print(food_expenses['Amount'].sum())
