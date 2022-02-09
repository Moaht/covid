from __future__ import annotations
import logging
import time
import flask
import news_data_handling
import covid_data_handler
import load_config

events = []
updates = []


def create_app() -> flask.app.Flask:
    """ Create WSGI flask app object.
    It is necessary for the website to display anything on the user's
        browser.
    This app object contains central registry for the view functions,
        URL rules and template configuration etc.

    :rtype: Returns a WSGI inherited flask object
    :return: flask.app.Flask
    """
    app = flask.Flask(__name__)
    return app
    

def render_index_page() -> None:
    """ Uses found data from the news and covid APIs
        populates a template index page with news articles
        about covid-19 as well as statistical data that is
        relevant to user specified areas.

    :return: Doesnt return anything.
    :rtype: None
    """
    config = load_config.open_user_config()
    return flask.render_template(
        'index.html',
        favicon="favicon.ico",
        title='Dashboard',
        location=(config['covid_minor']),
        nation_location=(config['covid_major']),
        # Show only 5 articles at a time
        news_articles=(
            news_data_handling.news_articles[
                :int(config['max_articles'])
                ]
            ),
        deaths_total=(
            covid_data_handler.covid_stats['deaths_total']
            ),
        hospital_cases=(
            covid_data_handler.covid_stats['hospital_cases']
            ),
        local_7day_infections=(
            covid_data_handler.covid_stats['local_7day_infections']
            ),
        national_7day_infections=(
            covid_data_handler.covid_stats['national_7day_infections']
            ),
        updates=updates,
        image=config['image']
    )


def calc_interval(update: str) -> int:
    """ Takes in time as HH:MM and compares it against current
    time to generate the interval between them in seconds

    :param update: String of time in HH:MM format
    :type update: str
    :return: Calculates interval in seconds from a time in
        HH:MM format
    :rtype: int
    """
    hours = update[0:2]
    mins = update[3:5]
    update = int(hours)*60*60 + int(mins)*60
    current = time.strftime("%H:%M", time.localtime())
    current = int(current[0:2])*60*60 + int(current[3:5])*60

    if update > current:
        interval = update - current
    else:
        interval = 24*60*60 + current - update
    logging.debug(
        "calc_interval used. Original time: %s,"
        " converted interval: %s",
        update, interval
        )
    return interval


def remove_expired_updates() -> None:
    """ Checks if an event is finished and if so,
    removes the event and update from their respective lists

    :return: Doesnt return anything.
    :rtype: None
    """

    for index in range(len(updates)-1, -1, -1):
        if updates[index]['type'] is None:
            # Identify and remove system notices for blank
            # update entry or init message
            logging.debug(
                "Removing system or error message: %s",
                updates[index]['title']
                )
            updates.pop(index)
        elif updates[index]['event'] not in covid_data_handler.s.queue and \
                updates[index]['event'] not in news_data_handling.s.queue:
            if updates[index]['type'] == 'covid_data' and \
                    updates[index]['repeat'] == 1:
                logging.debug(
                    "Recheduling covid data update: %s",
                    updates[index]['title']
                    )
                # remove old event from events list
                events.remove(updates[index]['event'])
                # append new event to events list
                events.append(covid_data_handler.schedule_covid_updates(
                    calc_interval(updates[index]['time']),
                    updates[index]['title'])
                )
                # put copy of event in dictionary
                updates[index]['event'] = events[-1]
            elif updates[index]['type'] == 'news' and \
                    updates[index]['repeat'] == 1:
                logging.debug(
                    "Recheduling news update: %s",
                    updates[index]['title']
                    )
                # remove old event from events list
                events.remove(updates[index]['event'])
                # append new event to events list
                events.append(news_data_handling.schedule_news_updates(
                    calc_interval(updates[index]['time']),
                    updates[index]['title'])
                )
                # put copy of event in dictionary
                updates[index]['event'] = events[-1]
            else:
                logging.debug(
                    "Removing update: %s",
                    updates[index]['title']
                    )
                events.remove(updates[index]['event'])
                updates.pop(index)


def serve_toast_covid_data(update, covid_data, two, repeat, news) -> None:
    """ Sets up covid data toast notifcations that are selected
        via the dashboard form 
        """
    if update and covid_data:
        covid_data_title = two + ' covid data update'
        events.append(covid_data_handler.schedule_covid_updates(
            calc_interval(update), covid_data_title)
            )
        updates.append(
            {
                'title': covid_data_title,
                'content': 'Scheduler set to update news at: ' + update,
                'event': events[-1],
                'time': update,
                'type': 'covid_data'
            }
        )
        logging.debug(
            "Added covid data update with name: %s"
            " set for %s",
            covid_data_title, update
        )
        if repeat:
            updates[-1]['repeat'] = 1
            updates[-1]['title'] = two + ' covid data update (repeat daily)'
        else:
            updates[-1]['repeat'] = 0
        if not news:
            pass
    flask.redirect('/index/', 302)


def serve_toast_news(update, news, two, repeat) -> None:
    """ Sets up news toast notifcations that are selected
        via the dashboard form 
        """
    if update and news:
        news_title = two + ' news update'
        events.append(news_data_handling.schedule_news_updates(
            calc_interval(update), news_title)
            )
        updates.append(
            {
                'title': news_title,
                'content': 'Scheduler set to update news at: ' + update,
                'event': events[-1],
                'time': update,
                'type': 'news'
            }
        )
        logging.debug(
            "Added news update with name: %s"
            " set for %s",
            news_title, update
        )
        if repeat:
            updates[-1]['repeat'] = 1
            updates[-1]['title'] = two + ' news update (repeat daily)'
        else:
            updates[-1]['repeat'] = 0


def set_form_error_msgs(update, news, covid_data) -> None:
    """ Sets error messages as toast notifications """
    if update and not news and not covid_data:
        updates.append(
            {
                'title': '449 Error - Insufficient input',
                'content': flask.Markup(
                    "<p style=\"color:red;\">No update was set. Please try \
                    again making sure to use the checkboxes provided to \
                    select an update.</p>"),
                'event': None,
                'time': update,
                'type': None
            }
        )
        logging.debug(
            "Setting '449 Error - Insufficient input' error message."
            )

    if not update and not updates:
        updates.append(
            {
                'title': 'No updates scheduled',
                'content': 'Use the form to schedule selected updates.',
                'event': None,
                'time': update,
                'type': None
            }
        )
        logging.debug(
            "Setting 'No updates scheduled' system message."
            )


def digest_toast(notif, update_item):
    """ Looks through news_articles list and removes
        an article from the list and from the scheduled
        updates list if necessary as well.
    """
    if notif:
        # Looks through news articles and removes the selected toast article
        # notifcation and adds it to a blacklist
        news_data_handling.remove_article(notif)
        logging.debug(
            "Removing article and adding to blacklist: %s", notif)

    if update_item:
        # Cancels selected scheduler event and removes
        # notification from dictionary
        for item in updates:
            if item['type'] == 'covid_data' and item['title'] == update_item:
                covid_data_handler.cancel_covid_update(item)
                events.remove(item['event'])
                updates.remove(item)
                logging.debug(
                    "Removing covid data event and nofication: %s", item)
            elif item['type'] == 'news' and item['title'] == update_item:
                news_data_handling.cancel_news_update(item)
                events.remove(item['event'])
                updates.remove(item)
                logging.debug(
                    "Removing news event and nofication: %s", item)


def request_handler() -> None:
    """ Handles the HTTP GET requests and pushes the 
        found data into various functions that uses
        the values as arguments

    :return: Doesnt return anything.
    :rtype: None
    """
    update = flask.request.args.get('update')
    two = flask.request.args.get('two')
    repeat = flask.request.args.get('repeat')
    covid_data = flask.request.args.get('covid-data')
    news = flask.request.args.get('news')
    update_item = flask.request.args.get('update_item')
    notif = flask.request.args.get('notif')

    news_data_handling.clear_newsapi_error_msgs()
    remove_expired_updates()
    serve_toast_covid_data(update, covid_data, two, repeat, news)
    serve_toast_news(update, news, two, repeat)
    set_form_error_msgs(update, news, covid_data)
    digest_toast(notif, update_item)


if __name__ == '__main__':
    pass
