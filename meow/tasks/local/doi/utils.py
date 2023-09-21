def generate_doi_external_label(protocol: str, domain: str, context: str, organization: str,
                                conference: str, contribution: str | None = None) -> str:
    return f"{protocol}://{domain}/{context}/{organization}-{conference}{('-' + contribution)}" \
        if contribution is not None else ''


def generate_doi_external_url(protocol: str, domain: str, context: str, organization: str,
                              conference: str, contribution: str | None = None) -> str:
    return f"{protocol}://{domain}/{context}/{organization}-{conference}{('-' + contribution)}".lower() \
        if contribution is not None else ''


def generate_doi_internal_url(organization: str, conference: str, contribution: str | None = None) -> str:
    return f"doi/{organization}-{conference}{('-' + contribution)}/index.html".lower() \
        if contribution is not None else ''


def generate_doi_identifier(context: str, organization: str, conference: str,
                            contribution: str | None = None) -> str:
    return f"{context}/{organization}-{conference}{('-' + contribution)}".lower() \
        if contribution is not None else ''


def generate_doi_name(context: str, organization: str, conference: str,
                      contribution: str | None) -> str:
    return f"{context}/{organization}-{conference}-{contribution}" \
        if contribution is not None else ''


def generate_doi_path(organization: str, conference: str, contribution: str) -> str:
    return f"{organization}-{conference}-{contribution}".lower()


def generate_doi_landing_page_url(organization: str, conference: str,
                                  contribution: str | None = None) -> str:
    return f"https://jacow.org/{conference}/doi/{organization}-{conference}{('-' + contribution)}" \
        if contribution is not None else ''
