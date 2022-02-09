from __future__ import annotations
import sched
import time
import requests
import flask
import load_config
import datetime
import logging
import simplejson

s = sched.scheduler(time.time, time.sleep)

news_articles = []
blacklist = []
config = load_config.open_user_config()


def remove_html_tags(article_content: str) -> str:
    """ Removes html tags in string text """
    logging.debug("Entered remove_html_tags")
    tag = False
    quote = False
    cleaned_article = ""

    for character in article_content:
        if character == '<' and not quote:
            tag = True
        elif character == '>' and not quote:
            tag = False
        elif character in ('"', "'") and tag:
            quote = not quote
        elif not tag:
            cleaned_article = cleaned_article + character
    logging.debug("Return value is: %s", cleaned_article)
    return cleaned_article


def news_API_request(
        covid_terms: str = "Covid COVID-19 coronavirus") -> dict[str]:
    """ Builds the URL to call the news API at newsapi.org, 
    sends the query and returns the retrieved json dictionary.
    The arguments for API can be set in the config.json file.
    If nothing is configured for the API, defaults will be used.
    """
    logging.debug("Entered news_API_request")
    logging.debug("covid_terms passed are: %s", covid_terms)

    url = ""

    # Adding URL stub
    if config['news_api_url_stub']:
        news_api_url_stub = config['news_api_url_stub']
        logging.debug(
            "Config loaded."
            " Using '%s' as criteria for news_api_url_stub",
            config['news_api_url_stub'])
        url = url + news_api_url_stub
    else:
        news_api_url_stub = 'https://newsapi.org/v2/everything?'
        logging.info(
            "'news_api_url_stub' not set in config."
            " Using default 'https://newsapi.org/v2/everything?' instead."
            )
        url = url + news_api_url_stub

    # Adding keywords to url query
    keywords = ' OR '.join(covid_terms.split())
    url = url + f'qInTitle={keywords}&'
    logging.info(
        "Using '%s' as criteria for keywords", keywords
        )

    # Adding domains to url query
    if config['domains']:
        domains = config['domains']
        logging.debug(
            "Config loaded."
            " Using '%s' as criteria for domains", config['domains']
            )
        url = url + f'domains={domains}&'

    # Adding sort rule to url query
    if config['sort']:
        sort = config['sort']
        logging.debug(
            "Config loaded."
            " Using '%s' as criteria for sort", config['sort']
            )
        url = url + f'sortBy={sort}&'
    else:
        sort = "relevancy"
        logging.info(
            "'sort' not set in config."
            " Using default 'relevancy' instead."
            )
        url = url + f'sortBy={sort}&'

    # Adding max_article_age to url query
    if config['max_article_age']:
        dt_now = datetime.datetime.now()
        days_to_subtract = datetime.timedelta(
            days=int(config['max_article_age'])
            )

        date = dt_now - days_to_subtract
        date = str(date)[:10]

        logging.debug(
            "Config loaded."
            " Using '%s' as criteria for max_article_age",
            config['max_article_age']
            )
        url = url + f'from={date}&'
    else:
        date = datetime.datetime.now()
        date = str(date)[:10]
        logging.info(
            "'max_article_age' not set in config."
            " Using default '0' instead."
            )
        url = url + f'from={date}&'

    # Adding news_lang to url query
    if config['news_lang']:
        news_lang = config['news_lang']
        logging.debug(
            "Config loaded."
            " Using '%s' as criteria for news_lang", config['news_lang']
            )
        url = url + f'language={news_lang}&'
    else:
        news_lang = "en"
        logging.info(
            "'news_lang' not set in config."
            " Using default 'en' instead."
            )
        url = url + f'language={news_lang}&'

    # Adding news_API_key to url query
    if config['news_API_key']:
        news_API_key = config['news_API_key']
        logging.debug(
            "Config loaded."
            " Found news_API_key."
            )
        url = url + f'apiKey={news_API_key}'
    else:
        logging.warning("'news_API_key' not set in config.")
        news_API_key = None

    # Finally, sending url query to news API
    logging.debug("Completed URL is : %s", url)

    response = requests.get(url)

    try:
        logging.debug("Return value is: %s", )
        return response.json()
    except simplejson.errors.JSONDecodeError:
        logging.error(
            "URL query failed. Check the URL in config and try again.",
            exc_info=True
            )
        logging.debug("Return value is: None")
        return None


def update_news(update_name: str) -> None:
    """ Updates the news_articles dictionary """
    logging.debug("Entered update_news")
    article_cache = news_API_request(
        config['news_keywords'])

    # Check if URL query was successful
    if article_cache is None:
        error_dict = {
            'title': "Error: URL query failed.",
            'content': " URL query wasn't received by server. \
                Check the URL in config.json and try again. To dismiss this \
                message, please click on the 'X' button on the top right."
        }
        news_articles.append(error_dict)
    # Check if the API params are valid
    elif article_cache['status'] == 'ok':
        article_cache = article_cache['articles']
        existing_list = []
        for article in news_articles:
            existing_list.append(article['title'])
        for entry in article_cache:
            # Checks for char count postscript and removes it
            if "chars]" in entry['content']:
                entry['content'] = remove_html_tags(
                    entry['content'][:entry['content'].index("[")])
            # Adds postscript with hyperlink to article source
            entry['content'] = entry['content'] + flask.Markup(
                "<a target=""blank"" rel=""noopener noreferrer"" href=\"" +
                entry['url'] + "\"> (Read More)</a> ")
            entry['sched_update_event'] = update_name
            if entry['title'] not in blacklist and \
                    entry['title'] not in existing_list:
                news_articles.append(entry)
    # If API params are invalid: display the error message returned by the API
    elif article_cache['status'] == 'error':
        error_dict = {
            'title': "Error: " + article_cache['code'],
            'content': f"{article_cache['message']} To dismiss this \
                message, please click on the 'X' button on the top right."
        }
        news_articles.append(error_dict)


def clear_newsapi_error_msgs() -> None:
    """ Checks if an error message (as an article) was displayed and
    removes the dictionary entry from the 'news_article' list
    """
    logging.debug("Entered clear_newsapi_error_msgs")
    for index in range(len(news_articles)-1, -1, -1):
        if 'error' in news_articles[index]:
            news_articles.pop(index)


def schedule_news_updates(
        update_interval: int, update_name: str) -> sched.Event:
    """ Sets events tonthe news scheduler """
    logging.debug("Entered schedule_news_updates")
    logging.debug("Scheduled update is called %s, update_inveral is %s", update_name, update_interval)
    return s.enter(update_interval, 1, update_news, {update_name: update_name})


def remove_article(notif: str) -> None:
    """ Removes news article from dashboard """
    logging.debug("Entered remove_article")
    for article in news_articles:
        if article['title'] == notif:
            logging.debug(
                "Removed and putting in blacklist article: \n%s",
                article['title']
                )
            blacklist.append(article['title'])
            news_articles.remove(article)
    logging.debug("Article blacklist is currently: \n%s", blacklist)            


def cancel_news_update(item: dict[str]) -> None:
    """ Cancels news update events """
    logging.debug("Entered cancel_news_update")
    s.cancel(item['event'])
    logging.debug("Cancelled news update is: %s", item)


def run_scheduled_news_updates() -> None:
    """ Runs scheduled news updates """
    logging.debug("Entered run_scheduled_news_updates")
    """ Run updates defined by schedule_news_updates """
    logging.debug("Current news scheduler queue is: %s", str(s.queue))
    s.run(blocking=False)


if __name__ == '__main__':
    pass
    # print(type(schedule_news_updates(1, "Test")))
    # print(update_news())
    # print(type(flask.redirect('/index')))