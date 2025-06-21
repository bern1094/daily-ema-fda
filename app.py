from flask import Flask, render_template_string
import requests
from bs4 import BeautifulSoup
from datetime import datetime

app = Flask(__name__)

def fetch_ema_approvals():
    url = "https://www.ema.europa.eu/en/news"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "lxml")
    
    today = datetime.now().strftime("%d/%m/%Y")
    items = soup.find_all("article")
    
    todays_articles = []

    for item in items:
        date_tag = item.find("time")
        if date_tag:
            article_date = date_tag.text.strip()
            if article_date == today:
                title = item.find("a").text.strip()
                link = "https://www.ema.europa.eu" + item.find("a")["href"]
                todays_articles.append((title, link))

    return todays_articles

def fetch_fda_approvals():
    url = "https://www.accessdata.fda.gov/scripts/cder/daf/index.cfm"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "lxml")
    
    today = datetime.now().strftime("%B %d, %Y")
    approvals = []

    table_rows = soup.find_all("tr")
    for row in table_rows:
        cells = row.find_all("td")
        if len(cells) >= 5:
            date = cells[4].text.strip()
            if date == today:
                drug = cells[0].text.strip()
                company = cells[1].text.strip()
                approvals.append(f"{drug} by {company}")

    return approvals

@app.route("/")
def home():
    ema = fetch_ema_approvals()
    fda = fetch_fda_approvals()

    html = """
    <h1>Daily EMA & FDA Submissions and Approvals</h1>
    <h2>EMA (Europe)</h2>
    {% if ema %}
        <ul>
        {% for title, link in ema %}
            <li><a href="{{ link }}" target="_blank">{{ title }}</a></li>
        {% endfor %}
        </ul>
    {% else %}
        <p>No updates today.</p>
    {% endif %}
    <h2>FDA (USA)</h2>
    {% if fda %}
        <ul>
        {% for item in fda %}
            <li>{{ item }}</li>
        {% endfor %}
        </ul>
    {% else %}
        <p>No updates today.</p>
    {% endif %}
    """
    return render_template_string(html, ema=ema, fda=fda)

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)

