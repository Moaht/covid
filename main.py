from __future__ import annotations
import logging
import flask
import covid_data_handler
import news_data_handling
import dashboard_functions
import load_config

app = dashboard_functions.create_app()

load_config.use_log()
logging.info("App initialised. Standing by to run.")


@app.errorhandler(404)
def page_not_found(err: int) -> callable:
    """ Handles URL queries that are unknown to the server (404)
    by returning a 404 page not found page.

    :param err: arg1
    :type a: int
    :rtype: callable
    :return: Calls 'render_template' from flask to render the
    '404.html' web page to the user's browser.
    """

    logging.error(
        '%s', err)

    return flask.render_template(
        '404.html', homepage=flask.url_for('.index')), 404


@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
@app.route('/index/', methods=['GET'])
def index() -> callable:
    """ Core function that runs the server.
    This function will be ran every 60 seconds due to the html template
    refresh rate. This is to create a loop that will keep running the
    event scheduler (sched).
    The 'request_handler' function will be ran to check for any GET requests
    containing data collected by user input on the form displayed by the
    index template.
    If there are any events queued, then they will be ran via the
    'run_scheduled_news_updates' and 'run_scheduled_covid_updates' function
    calls.

    :rtype: callable
    :return: Calls the 'render_index_page' function to render the
    'index.html' web page to the user's browser.
    """
    logging.info(
        "Page refresh or user requested root/index page."
        " Data may have been updated.")

    news_data_handling.run_scheduled_news_updates()
    covid_data_handler.run_scheduled_covid_updates()
    dashboard_functions.request_handler()

    return dashboard_functions.render_index_page()


if __name__ == '__main__':
    logging.info("App started running.")
    app.run()
    logging.info("App has stopped.")
