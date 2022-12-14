import os
import requests
import smtplib


STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"
NOTIFICATION_BASELINE = 2
EMAIL_SMTP = "smtp.gmail.com"
ARTICLE_COUNT = 3


def get_stock_change():
    # AV, Alpha Vantage Stock APIs
    AV_parameters = {
        "function": "TIME_SERIES_DAILY",
        "symbol": STOCK,
        "outputsize": "compact",
        "apikey": os.environ.get("AV_API_KEY")
    }

    response = requests.get("https://www.alphavantage.co/query", params=AV_parameters)
    response.raise_for_status()
    AV_data = response.json()["Time Series (Daily)"]
    stock_prices = [data for (key, data) in AV_data.items()]

    day1_prior_price = float(stock_prices[0]["4. close"])
    day2_prior_price = float(stock_prices[1]["4. close"])

    percentage_change = ((day1_prior_price - day2_prior_price) / day2_prior_price) * 100
    return percentage_change


def get_news():
    news_parameters = {
        "apiKey": os.environ.get("NEWS_API_KEY"),
        "q": COMPANY_NAME,
        "language": "en",
        "sortBy": "publishedAt",
    }

    response = requests.get("https://newsapi.org/v2/everything", news_parameters)
    news_data = response.json()["articles"]
    return news_data


if abs(get_stock_change()) >= NOTIFICATION_BASELINE:

    # TODO: Have an option to send to SMS rather than email once Twilio is verified
    if get_stock_change() < 0:
        stock_format = "🔻 " + str(abs(round(get_stock_change(), 3))) + "%"
    elif get_stock_change() > 0:
        stock_format = "🔺 " + str(abs(round(get_stock_change(), 3))) + "%"

    news = get_news()
    articles = news[0:ARTICLE_COUNT]
    mail_contents = f"Subject: {COMPANY_NAME} ({STOCK}): {stock_format}\n\n"
    for article in articles:
        mail_contents += f"{article['title']}\n- {article['description']}\n{article['url']}\n\n"

    from_email = os.environ.get("FROM_EMAIL")
    to_email = os.environ.get("TO_EMAIL")
    password = os.environ.get("PASSWORD")

    with smtplib.SMTP(EMAIL_SMTP, 587) as connection:
        connection.starttls()
        connection.login(from_email, password)
        connection.sendmail(from_addr=from_email, to_addrs=to_email,
                            msg=mail_contents.encode('utf-8'))
