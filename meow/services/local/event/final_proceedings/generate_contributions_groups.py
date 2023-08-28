import logging as lg

from anyio import create_task_group, CapacityLimiter

from meow.models.local.event.final_proceedings.event_model import AffiliationData, KeywordData, PersonData

from meow.models.local.event.final_proceedings.proceedings_data_model import ProceedingsData
from meow.models.local.event.final_proceedings.track_model import TrackData


logger = lg.getLogger(__name__)


async def generate_contributions_groups(proceedings_data: ProceedingsData,
                                        cookies: dict, settings: dict) -> ProceedingsData:
    """ """

    logger.info('event_final_proceedings - generate_contributions_groups')

    capacity_limiter = CapacityLimiter(16)

    async with create_task_group() as tg:
        tg.start_soon(contributions_group_by_session,
                      capacity_limiter, proceedings_data, cookies, settings)
        tg.start_soon(contributions_group_by_classification,
                      capacity_limiter, proceedings_data, cookies, settings)
        tg.start_soon(contributions_group_by_author,
                      capacity_limiter, proceedings_data, cookies, settings)
        tg.start_soon(contributions_group_by_institute,
                      capacity_limiter, proceedings_data, cookies, settings)
        tg.start_soon(contributions_group_by_doi_per_institute,
                      capacity_limiter, proceedings_data, cookies, settings)
        tg.start_soon(contributions_group_by_keyword,
                      capacity_limiter, proceedings_data, cookies, settings)

    # proceedings_data = await contributions_group_by_session(proceedings_data, cookies, settings)
    # proceedings_data = await contributions_group_by_classification(proceedings_data, cookies, settings)
    # proceedings_data = await contributions_group_by_author(proceedings_data, cookies, settings)
    # proceedings_data = await contributions_group_by_institute(proceedings_data, cookies, settings)
    # proceedings_data = await contributions_group_by_doi_per_institute(proceedings_data, cookies, settings)
    # proceedings_data = await contributions_group_by_keyword(proceedings_data, cookies, settings)

    # logger.info(json_encode(proceedings_data.classification))    #
    # logger.info(json_encode(proceedings_data.author))    #
    # logger.info(json_encode(proceedings_data.institute))    #
    # logger.info(json_encode(proceedings_data.keyword))

    return proceedings_data


async def contributions_group_by_session(capacity_limiter: CapacityLimiter, proceedings_data: ProceedingsData,
                                         cookies: dict, settings: dict) -> ProceedingsData:
    """ """

    async with capacity_limiter:
        pass

    return proceedings_data


async def contributions_group_by_classification(capacity_limiter: CapacityLimiter, proceedings_data: ProceedingsData,
                                                cookies: dict, settings: dict) -> ProceedingsData:
    """ """

    async with capacity_limiter:

        classification_list: list[TrackData] = []

        for contribution in proceedings_data.contributions:
            if contribution.track is not None and contribution.track not in classification_list:
                classification_list.append(contribution.track)

        classification_list = list(set(classification_list))

        def classification_sort(x: TrackData) -> str:
            return (f"{x.track_group.position:03d}_{x.track_group.name}_{x.position:03d}_{x.name}"
                    if x.track_group else f"default_000_{x.position:03d}_{x.name}").lower()

        classification_list.sort(key=classification_sort)

        proceedings_data.classification = classification_list

    return proceedings_data


async def contributions_group_by_author(capacity_limiter: CapacityLimiter, proceedings_data: ProceedingsData,
                                        cookies: dict, settings: dict) -> ProceedingsData:
    """ """

    async with capacity_limiter:

        author_list: list[PersonData] = []

        for contribution in proceedings_data.contributions:
            for author in contribution.authors:
                if author is not None and author not in author_list:
                    author_list.append(author)

        author_list = list(set(author_list))

        author_list.sort(
            key=lambda x: f"{x.last} {x.first} {x.affiliation}".lower())

        proceedings_data.author = author_list

    return proceedings_data


async def contributions_group_by_institute(capacity_limiter: CapacityLimiter, proceedings_data: ProceedingsData,
                                           cookies: dict, settings: dict) -> ProceedingsData:
    """ """

    async with capacity_limiter:

        institute_list: list[AffiliationData] = []

        for contribution in proceedings_data.contributions:
            for institute in contribution.institutes:
                if institute is not None and institute not in institute_list:
                    institute_list.append(institute)

        institute_list = list(set(institute_list))

        institute_list.sort(key=lambda x: f"{x.name}".lower())

        proceedings_data.institute = institute_list

    return proceedings_data


async def contributions_group_by_doi_per_institute(capacity_limiter: CapacityLimiter, proceedings_data: ProceedingsData,
                                                   cookies: dict, settings: dict) -> ProceedingsData:
    """ """

    return proceedings_data


async def contributions_group_by_keyword(capacity_limiter: CapacityLimiter, proceedings_data: ProceedingsData,
                                         cookies: dict, settings: dict) -> ProceedingsData:
    """ """

    async with capacity_limiter:

        keyword_list: list[KeywordData] = []

        for contribution in proceedings_data.contributions:
            for keyword in contribution.keywords:
                if keyword is not None and keyword not in keyword_list:
                    keyword_list.append(keyword)

        keyword_list = list(set(keyword_list))

        keyword_list.sort(key=lambda x: f"{x.name}".lower())

        proceedings_data.keyword = keyword_list

    return proceedings_data
