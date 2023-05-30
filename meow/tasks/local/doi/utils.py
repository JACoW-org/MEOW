def generate_doi_url(protocol: str, domain: str, context: str, organization: str, conference: str, contribution: str) -> str:
    return f"{protocol}://{domain}/{context}/{organization}-{conference}-{contribution}"

def generate_doi_identifier(context: str, organization: str, conference: str, contribution: str) -> str:
    return f"{context}/{organization}-{conference}-{contribution}"

def generate_doi_path(organization: str, conference: str, contribution: str) -> str:
    return f"{organization}-{conference}-{contribution}"