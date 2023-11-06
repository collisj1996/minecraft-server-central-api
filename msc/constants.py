from enum import Enum

CDN_DOMAIN = "cdn.minecraftservercentral.com"

ALLOWED_TAGS = [
    "factions",
    "hungergames",
    "economy",
    "skyblock",
    "survivalgames",
    "mcmmo",
    "prison",
    "survival",
    "creative",
    "hardcore",
    "adventure",
    "vanilla",
    "semi-vanilla",
    "semivanilla",
    "bukkit",
    "spigot",
    "pve",
    "pvp",
    "rpg",
]


ADMIN_USER_IDS = [
    "d24544e4-b0a1-7007-f8cf-9efb4eb35d8a",  # jc
    "82150464-d0e1-7018-a2ae-4d4f3e80ab92",  # mg
]

ASYNC_POLL_BATCH_SIZE = 20

MINIMUM_BID_DEFAULT = 10
SPONSORED_SLOTS_DEFAULT = 10

DEFAULT_AUCTION_PAGE_SIZE = 10
DEFAULT_AUCTION_PAGE = 1
MAX_AUCTIONS_PAGE_SIZE = 10


SERVER_LIST_SERVICE_NAME = "MCSC"

QUERY_STRING_TAG_LIST_MAX = 10
QUERY_STRING_VERSION_LIST_MAX = 10

EMAIL_SENDER = "minecraftservercentralofficial@gmail.com"


class BidPaymentStatus(str, Enum):
    """Enum for bid status"""

    PAID = "Paid"
    AWAITING_PAYMENT = "Awaiting Payment"
    FORFEIT = "Forfeit"
    AWAITING_RESPONSE = "Awaiting Response"
    STANDBY = "Standby"
