# Run a test server.
from ssportal import app
import logging
from logging.handlers import RotatingFileHandler
import os

try:
    port = int(os.getenv("PORT"))
except:
    port = 5000


SITE_ROOT = os.path.dirname(os.path.realpath(__file__))


if __name__ == '__main__':
    app.debug=True
    LOG_FILENAME = os.path.join((os.path.join(SITE_ROOT, 'logs')), 'ssportal.log')

    formatter = logging.Formatter(
        "[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s")
    handler = RotatingFileHandler(LOG_FILENAME, maxBytes=10000000, backupCount=5)
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)

    app.run(host='0.0.0.0', port=port)


##ad comment line
