import logging as lg

from meow.models.local.event.final_proceedings.proceedings_data_model import ProceedingsData

logger = lg.getLogger(__name__)


async def check_sessions_without_code(proceedings_data: ProceedingsData) -> list[str]:
    """Detect sessions without a code that have contributions.

    The site publishes such a session under its id only (``session/<id>/``,
    see JACoW-org/MEOW#39), without the code in its name and title. The
    editors are warned so that they can set the code in Indico. Not blocking.
    """

    logger.info("event_final_proceedings - check_sessions_without_code")

    warnings: list[str] = []

    for session in proceedings_data.sessions:
        if not session or session.code:
            continue

        codes = sorted(
            c.code for c in proceedings_data.contributions
            if c.session_id == session.id and c.code
        )
        if not codes:
            continue

        warnings.append(
            f"Session without code: session {session.id} '{session.title}' "
            f"has no code, so its page in the site is named after the id only "
            f"(session/{session.id}/): {', '.join(codes)}."
        )

    logger.warning(f"check_sessions_without_code: {len(warnings)} warning(s) found.")
    for w in warnings:
        logger.warning(w)

    return warnings
