# 📦 Step 1: Import libraries
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# 🏠 Step 2: Input data (Area,NO.of Bedrooms,NO. of Washrooms)
X = np.array([
    [1200, 3, 10],
    [1500, 4, 5],
    [1800, 4, 2],
    [1000, 2, 20],
    [2000, 5, 1]
])  # Each row = [area,NO.of Bedrooms,NO. of Washrooms]

# 🎯 Step 3: Target prices (in ₹ thousands)
y = np.array([300, 400, 500, 250, 550])

# 🧠 Step 4: Create and train the model
model = LinearRegression()
model.fit(X, y)  # model learns the best values from data

# 📈 Step 5: Predict prices using the same data
y_pred = model.predict(X)

# ✅ Step 6: Evaluate the model
mae = mean_absolute_error(y, y_pred)        # Avg. error
mse = mean_squared_error(y, y_pred)         # Squared error
rmse = np.sqrt(mse)                         # Root MSE
r2 = r2_score(y, y_pred)                    # R² score

k=int(input("Enter area of NewHouse:"))
t=int(input("Enter NO of Bedrooms in NewHouse:"))
j=int(input("Enter No of Washrooms in NewHouse:"))
NewHouse=np.array([[k,t,j]])
PredictedPrice=model.predict(NewHouse)
print(f"Predicted price for {k} sq.ft = ₹{PredictedPrice[0]*100000}")



# 🖨️ Print results
print("🔢 Coefficients:", model.coef_)
print("⚓ Intercept:", model.intercept_)
print("📏 MAE (Mean Absolute Error):", mae)
print("📏 RMSE (Root Mean Squared Error):", rmse)
print("📊 R² Score:", r2)

# 🖼️ Step 7: Plot Actual vs Predicted Prices
plt.figure(figsize=(10, 5))
plt.scatter(range(len(y)), y, color='blue', label='Actual Prices')      # Blue = actual
plt.plot(range(len(y_pred)), y_pred, color='red', label='Predicted Prices')  # Red = model
plt.title("Actual vs Predicted House Prices")
plt.xlabel("House Index")
plt.ylabel("Price (in ₹ Thousands)")
plt.legend()
plt.grid(True)
plt.show()

# 🖼️ Step 8: Plot Residuals (how far off the predictions were)
residuals = y - y_pred  # error = actual - predicted
plt.figure(figsize=(10, 4))
plt.scatter(range(len(residuals)), residuals, color='purple')
plt.axhline(y=0, color='black', linestyle='--')  # Line at zero error
plt.title("Residual Plot (Error for Each House)")
plt.xlabel("House Index")
plt.ylabel("Error (Actual - Predicted)")
plt.grid(True)
plt.show()
