
from json import dumps

from tests.group.data import contributions as data


async def contribution_to_item(contribution: dict) -> dict:
    return dict(
        code=contribution.get('code')
    )


async def group_by_session(contributions: list):

    groups = {}

    for contribution in contributions:

        group_code: list[str] = [contribution.get('session', '')]
        group_key: str = repr(group_code)

        if group_key not in groups:
            groups[group_key] = {
                'code': group_code,
                'items': []
            }

        groups[group_key].get('items').append(
            await contribution_to_item(contribution))

    print(dumps(groups, indent=2))


async def group_by_track(contributions: list):

    groups = {}

    for contribution in contributions:

        group_code: list[str] = contribution.get('track', [])
        group_key: str = repr(group_code)

        if group_key not in groups:
            groups[group_key] = {
                'code': group_code,
                'items': []
            }

        groups[group_key].get('items').append(
            await contribution_to_item(contribution))

    print(dumps(groups, indent=2))


async def group_by_author(contributions: list):

    groups = {}

    for contribution in contributions:

        group_codes: list[str] = contribution.get('authors', [])

        for group_code in group_codes:
            group_key: str = repr([group_code])

            if group_key not in groups:
                groups[group_key] = {
                    'code': group_code,
                    'items': []
                }

            groups[group_key].get('items').append(
                await contribution_to_item(contribution))

    print(dumps(groups, indent=2))


async def main():
    await group_by_session(data)
    print("\n\n")
    await group_by_track(data)
    print("\n\n")
    await group_by_author(data)
    print("\n\n")
