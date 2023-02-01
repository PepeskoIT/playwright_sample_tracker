from logging import getLogger
from os.path import join

from settings import DATA_FOLDER, PGG_DATA_FOLDER, TAURON_DATA_FOLDER

logger = getLogger("buy-bot")

DATE_FORMAT = "%d-%m-%Y_%H%M%S"

SHOP_FOLDERS = {
    "PggBuy": join(DATA_FOLDER, PGG_DATA_FOLDER),
    "TauronBuy": join(DATA_FOLDER, TAURON_DATA_FOLDER)
}


LOGIN_ENDPOINT = "/login"