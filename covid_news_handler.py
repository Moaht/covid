from time import strftime, gmtime
import requests
from covid_data_handler import covid_API_request


def news_API_request(covid_terms="Covid COVID-19 coronavirus"):
    """Takes in keywords, splits them and sends off to api for news"""
    keywords = " OR ".join(covid_terms.split())
    date = strftime("%Y-%m-%d", gmtime())

    url = (
        'https://newsapi.org/v2/everything?'
        f'qInTitle={keywords}&'
        f'from={date}&'
        'language=en&'
        'sortBy=relevancy&'
        'apiKey=a8dcbe2b66d242a5a4e963e9c0363716'
        )
    
    response = requests.get(url)
    return response

def update_news():

    #use news_API_request to get news
    #put news into data structure containing articles
    #integrate this with schedule_covid_updates to periodically get updated news
    # (news needs to be updated at a different interval than covid data)
    #there is way to "remove" articles you have already seen from the interface.
    # the removed articles shouldn't reappear when news is updated