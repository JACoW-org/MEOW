import string

from meow.models.local.event.final_proceedings.event_model import (AffiliationData, KeywordData,
    PersonData)

def group_authors_by_last_initial_for_render(authors: list[PersonData]) -> dict:
    """"""

    groups = {}
    for author in authors:
        key = author.last[0].lower() if author.last else author.first[0].lower()
        if key not in groups:
            groups[key] = []
        groups[key].append(author.as_dict())
    return groups

def group_keywords_by_initial(keywords: list[KeywordData]) -> dict:
    """"""

    groups = {}
    for keyword in keywords:
        key = keyword.name[0].lower()
        if key not in groups:
            groups[key] = []
        groups[key].append(keyword.as_dict())

    return groups

def group_institutes_by_initial(institutes: list[AffiliationData]) -> dict:
    """"""

    groups = {}
    for institute in institutes:
        if institute.name:
            key = institute.name[0].lower()
            if key not in groups:
                groups[key] = []
            groups[key].append(institute.as_dict())
    return groups

def get_authors_initials_dict(authors: list[PersonData]) -> dict[str, bool]:
    """"""
    
    initials = {}

    # set with letters from the alphabet
    alphabet = set(string.ascii_lowercase)

    # init initials
    for letter in alphabet:
        initials[letter] = False

    # iterate over authors to build map of initials
    for author in authors:
        initial = author.last[0].lower() if author.last else author.first[0].lower()
        initials[initial] = True

    return initials

def get_keywords_initials_dict(keywords: list[KeywordData]) -> dict[str, bool]:
    """"""

    initials = {}

    # set with letters from the alphabet
    alphabet = set(string.ascii_lowercase)

    # init initials
    for letter in alphabet:
        initials[letter] = False

    for keyword in keywords:
        initial = keyword.name[0].lower()
        initials[initial] = True

    return initials

def get_institutes_initials_dict(institutes: list[AffiliationData]) -> dict[bool]:
    """"""

    initials = {}

    # set with letters from the alphabet
    alphabet = set(string.ascii_lowercase)

    # init initials
    for letter in alphabet:
        initials[letter] = False

    for institute in institutes:
        if institute.name:
            initial = institute.name[0].lower()
            initials[initial] = True

    return initials