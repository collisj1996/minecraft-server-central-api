import logging

import requests

logger = logging.getLogger(__name__)


def get_token(code: str, redirect_url: str):
    try:
        params = {
            "grant_type": "authorization_code",
            "client_id": "it0ectnsd44cr1phrifio2h5k",
            "redirect_uri": redirect_url,
            "code": code,
        }

        result = requests.post(
            "https://minecraftservercentral.auth.eu-west-1.amazoncognito.com/oauth2/token",
            params=params,
            headers={"content-type": "application/x-www-form-urlencoded;charset=utf-8"},
        )

        return result.json()
    except Exception as e:
        logging.error(e)
        raise e


def refresh_token(refresh_token: str):
    try:
        params = {
            "grant_type": "refresh_token",
            "client_id": "it0ectnsd44cr1phrifio2h5k",
            "refresh_token": refresh_token,
        }

        result = requests.post(
            "https://minecraftservercentral.auth.eu-west-1.amazoncognito.com/oauth2/token",
            params=params,
            headers={"content-type": "application/x-www-form-urlencoded;charset=utf-8"},
        )

        return result.json()
    except Exception as e:
        logging.error(e)
        raise e
