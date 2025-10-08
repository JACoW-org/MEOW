DATA_API_PROD = "api.datacite.org"
DATA_API_TEST = "api.test.datacite.org"


def get_doi_api_login(settings: dict) -> str:
    return settings.get("doi_user", "")


def get_doi_api_password(settings: dict) -> str:
    return settings.get("doi_password", "")


def get_doi_api_url(settings: dict, doi_id: str) -> str:
    doi_env = settings.get("doi_env", "test")
    doi_api = DATA_API_PROD if doi_env == "prod" else DATA_API_TEST
    doi_url = f"https://{doi_api}/dois/{doi_id}".lower()

    return doi_url


def get_doi_login_url(settings: dict) -> str:
    doi_env = settings.get("doi_env", "test")
    doi_api = DATA_API_PROD if doi_env == "prod" else DATA_API_TEST
    doi_url = f"https://{doi_api}/token".lower()

    return doi_url
