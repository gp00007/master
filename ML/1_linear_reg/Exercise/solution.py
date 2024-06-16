# EXERCISE

import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

# Creating the DataFrame with the provided data
df = pd.read_csv("C:\\Users\\user\\Downloads\\.csv")

# Visualizing the data
plt.xlabel("Year")
plt.ylabel("Per Capita Income (US$)")
plt.scatter(df['year'], df['per capita income (US$)'], color='black', marker='+')
plt.show()

# Training the linear regression model
reg = LinearRegression()
reg.fit(df[['year']], df['per capita income (US$)'])

# Predicting the per capita income for 2020
predicted_income_2020 = reg.predict([[2020]])
print(f"Predicted Per Capita Income for 2020: ${predicted_income_2020[0]:.2f}")

