def generate_doi_url(base_url: str, conference_code: str, contribution_code: str) -> str:
    return f"{base_url}/JACoW-{conference_code}-{contribution_code}"