import logging as lg

from anyio import Path

from meow.models.local.event.final_proceedings.proceedings_data_model import (
    ProceedingsData)
from meow.utils.filesystem import copy


logger = lg.getLogger(__name__)


async def copy_html_partials(proceedings_data: ProceedingsData,
                             cookies: dict, settings: dict) -> ProceedingsData:
    """ """

    await copy_html_files(proceedings_data)
    await copy_json_files(proceedings_data)

    return proceedings_data


async def copy_json_files(proceedings_data: ProceedingsData):

    html_dir_name = f"{proceedings_data.event.id}_src"
    html_base_dir: Path = Path("var", "run", html_dir_name)
    
    inspirehep_name = f'{proceedings_data.event.id}_inspirehep'
    inspirehep_dir = Path('var', 'run', f'{inspirehep_name}')

    json_dest_dir: Path = Path(html_base_dir, "static", "json")

    await json_dest_dir.mkdir(exist_ok=True, parents=True)

    json_src = Path(inspirehep_dir, 'inspirehep.jsonl')
    json_dest = Path(json_dest_dir, 'inspirehep.jsonl')

    if await json_dest.exists():
        await json_dest.unlink()

    await copy(str(json_src), str(json_dest))


async def copy_html_files(proceedings_data: ProceedingsData):

    html_dir_name = f"{proceedings_data.event.id}_src"
    html_base_dir: Path = Path("var", "run", html_dir_name)
    html_dest_dir: Path = Path(html_base_dir, "static", "html")

    await html_dest_dir.mkdir(exist_ok=True, parents=True)

    logger.info(f"{html_dest_dir} created!")

    partials = [
        {"name": "author_list.html", "src": Path(
            "layouts", "partials", "author", "list.html")},
        {"name": "classification_list.html", "src": Path(
            "layouts", "partials", "classification", "list.html")},
        {"name": "doi_per_institute_list.html", "src": Path(
            "layouts", "partials", "doi_per_institute", "list.html")},
        {"name": "institute_list.html", "src": Path(
            "layouts", "partials", "institute", "list.html")},
        {"name": "keyword_list.html", "src": Path(
            "layouts", "partials", "keyword", "list.html")},
        {"name": "session_list.html", "src": Path(
            "layouts", "partials", "session", "list.html")},
    ]

    for partial in partials:
        html_src = Path(html_base_dir, partial.get('src', ''))
        html_dest = Path(html_dest_dir, partial.get('name', ''))

        if await html_dest.exists():
            await html_dest.unlink()

        await copy(str(html_src), str(html_dest))
