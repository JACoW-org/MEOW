
import pathlib
from odf.opendocument import load
from itertools import groupby
from operator import itemgetter


async def async_load():

    contribution_primary_authors_list = [
        {'first': 'Andrei', 'last': 'Trebushinin',
            'affiliation': 'European XFEL GmbH'},
        {'first': 'Gianluca', 'last': 'Geloni',
            'affiliation': 'European XFEL GmbH'},
        {'first': 'Svitozar', 'last': 'Serkez',
            'affiliation': 'European XFEL GmbH'},
        {'first': 'Marc', 'last': 'Guetg',
            'affiliation': 'Deutsches Elektronen-Synchrotron'},
        {'first': 'Evgeny', 'last': 'Schneidmiller',
            'affiliation': 'Deutsches Elektronen-Synchrotron'},
    ]

    print(contribution_primary_authors_list)
    print()

    contribution_primary_authors_groups: list[dict[str, dict]] = [
        ({'key': key, 'items': [item for item in items]})

        for (key, items) in groupby(contribution_primary_authors_list,
                                    itemgetter('affiliation'))
    ]

    print(contribution_primary_authors_groups)
    print()

    contribution_primary_authors_values = [
        (
            f"{item.get('first', '')} {item.get('last')} ({item.get('affiliation')})"
            if index == len(g.get('items', []))-1 else f"{item.get('first')} {item.get('last')}"
        )        
        for g in contribution_primary_authors_groups                
        for index, item in enumerate(g.get('items', []))        
    ]
    
    print(contribution_primary_authors_values)
    print()

    contribution_primary_authors_value = ', '.join(
        contribution_primary_authors_values)

    print(contribution_primary_authors_value)
