import string

from unidecode import unidecode

from meow.models.local.event.final_proceedings.event_model import (
    AffiliationData,
    KeywordData,
    PersonData,
)


def group_authors_by_last_initial_for_render(authors: list[PersonData]) -> dict:
    """ """

    # reduce authors that appear with different instances (for example with different affiliations)
    flat_authors: dict[str, dict] = {}
    for author in authors:
        if author.id in flat_authors:
            flat_authors[author.id]["affiliations"] = list(
                set(author.affiliations + flat_authors[author.id]["affiliations"])
            )
        else:
            flat_authors[author.id] = author.as_dict()

    # set with letters from the alphabet
    alphabet = set(string.ascii_lowercase)

    groups = {}

    for author in flat_authors.values():
        if author["last"]:
            key = get_initial(author["last"], alphabet)
        else:
            key = get_initial(author["first"], alphabet)

        if key not in groups:
            groups[key] = []

        groups[key].append(author)

    # for author in authors:
    #     key = get_initial(author.last, alphabet) if author.last else get_initial(
    #         author.first, alphabet)
    #     if key not in groups:
    #         groups[key] = []
    #     groups[key].append(author.as_dict())

    return groups


def group_keywords_by_initial(keywords: list[KeywordData]) -> dict:
    """ """

    # set with letters from the alphabet
    alphabet = set(string.ascii_lowercase)

    groups = {}
    for keyword in keywords:
        key = get_initial(keyword.name, alphabet)
        if key not in groups:
            groups[key] = []
        groups[key].append(keyword.as_dict())

    return groups


def group_institutes_by_initial(institutes: list[AffiliationData]) -> dict:
    """"""

    # set with letters from the alphabet
    alphabet = set(string.ascii_lowercase)

    groups = {}
    for institute in institutes:
        if institute.name:
            key = get_initial(institute.name, alphabet)
            if key not in groups:
                groups[key] = []
            groups[key].append(institute.as_dict())
    return groups


def get_authors_initials_dict(authors: list[PersonData]) -> dict[str, bool]:
    """ """

    initials = {}

    # set with letters from the alphabet
    alphabet = set(string.ascii_lowercase)

    # init initials
    for letter in alphabet:
        initials[letter] = False

    # iterate over authors to build map of initials
    for author in authors:
        initial = (
            get_initial(author.last, alphabet)
            if author.last
            else get_initial(author.first, alphabet)
        )
        initials[initial] = True

    return initials


def get_keywords_initials_dict(keywords: list[KeywordData]) -> dict[str, bool]:
    """ """

    initials = {}

    # set with letters from the alphabet
    alphabet = set(string.ascii_lowercase)

    # init initials
    for letter in alphabet:
        initials[letter] = False

    for keyword in keywords:
        initial = get_initial(keyword.name, alphabet)
        initials[initial] = True

    return initials


def get_institutes_initials_dict(institutes: list[AffiliationData]) -> dict[str, bool]:
    """ """

    initials = {}

    # set with letters from the alphabet
    alphabet = set(string.ascii_lowercase)

    # init initials
    for letter in alphabet:
        initials[letter] = False

    for institute in institutes:
        if institute.name:
            initial = get_initial(institute.name, alphabet)
            initials[initial] = True

    return initials


def get_initial(name, alphabet):
    if not name:
        return "*"

    initial = unidecode(name)[0].lower()

    if initial not in alphabet:
        return get_initial(name[1:], alphabet)

    return initial
