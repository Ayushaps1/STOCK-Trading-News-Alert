import requests
from datetime import date
from twilio.rest import Client

STOCK = "TSLA"
COMPANY_NAME = "tesla"

stock_api_endpoint = "https://www.alphavantage.co/query"
news_api_endpoint = "https://newsapi.org/v2/everything"

news_api_key = os.environ.get("NEWS_API_KEY")
stock_api_key = os.environ.get("STOCK_API_KEY")

account_sid = os.environ.get("ACCOUNT_SID")
auth_token = os.environ.get("AUTH_TOKEN")

#########--------------Getting the change in stock price------------###########


stock_params = {
    "function": "TIME_SERIES_DAILY",
    "symbol": STOCK,
    "apikey": stock_api_key
}

response = requests.get(stock_api_endpoint, params=stock_params)
response.raise_for_status()
stock_data = response.json()

daily_data_list = list(stock_data["Time Series (Daily)"].values())

yesterdays_closing_price = float(daily_data_list[0]['4. close'])
day_before_yesterday_closing_price = float(daily_data_list[1]['4. close'])

change_in_price = yesterdays_closing_price - day_before_yesterday_closing_price
change_in_percentage = float("{:.2f}".format(abs(change_in_price) / yesterdays_closing_price * 100))

change = "🔺"
if change_in_price < 0:
    change = "🔻"

if change_in_price > 5:
    # ------Getting News Data of Tesla--------- #
    current_date = date.today()
    news_params = {
        "qInTitle": COMPANY_NAME,
        "from": current_date,
        "sortBy": "publishedAt",
        "language": "en",
        "apiKey": news_api_key
    }

    response = requests.get(news_api_endpoint, params=news_params)
    response.raise_for_status()
    news_data = response.json()
    news_list = news_data["articles"][:3]

    news_msg = ""
    for news in news_list:
        news_msg += f"Headlines: {news['title']}\n"
        news_msg += f"Brief: {news['description']}\n\n"

    # ------------Sending an alert through SMS----------- #
    client = Client(account_sid, auth_token)
    message = client.messages \
        .create(
        body=f"{STOCK}: {change}{change_in_percentage}%\n{news_msg}",
        from_='+18126355246',
        to='+918305262499'
    )

    print(message.sid)
