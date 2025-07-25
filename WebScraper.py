import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

# List of stock symbols (you can add more)
stocks = {
    "TCS": "TCS.NS",
    "Reliance": "RELIANCE.NS",
    "Infosys": "INFY.NS"
}

data = []

for name, symbol in stocks.items():
    url = f"https://finance.yahoo.com/quote/{symbol}"
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    try:
        price = soup.find("fin-streamer", {"data-field": "regularMarketPrice"}).text
        change = soup.find("fin-streamer", {"data-field": "regularMarketChangePercent"}).text

        data.append({
            "Company": name,
            "Symbol": symbol,
            "Price (INR)": price,
            "Change (%)": change,
        })

    except Exception as e:
        print(f"Failed to fetch data for {name}: {e}")

# Convert to DataFrame
df = pd.DataFrame(data)

# Save to Excel
filename = f"stock_report_{datetime.now().strftime('%Y-%m-%d_%H-%M')}.xlsx"
df.to_excel(filename, index=False)

print(f"Stock report saved as {filename}")
import smtplib
from email.message import EmailMessage
import os

# Email config
sender_email = "sender email"
receiver_email = "receiver email"
password = "enter your password"

# File to attach
attachment_path = filename  # from previous part

# Create the email
msg = EmailMessage()
msg["Subject"] = "📈 Daily Stock Market Report"
msg["From"] = sender_email
msg["To"] = receiver_email
msg.set_content("Hi,\n\nAttached is your daily stock market report generated by Python automation.\n\n- Sent via Bot 😎")

# Read and attach Excel file
with open(attachment_path, "rb") as f:
    file_data = f.read()
    file_name = os.path.basename(attachment_path)
    msg.add_attachment(file_data, maintype="application", subtype="vnd.openxmlformats-officedocument.spreadsheetml.sheet", filename=file_name)

# Send the email
try:
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(sender_email, password)
        smtp.send_message(msg)
        print("✅ Email sent successfully!")
except Exception as e:
    print("❌ Failed to send email:", e)
