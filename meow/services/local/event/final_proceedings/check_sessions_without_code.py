import logging as lg

from meow.models.local.event.final_proceedings.proceedings_data_model import ProceedingsData

logger = lg.getLogger(__name__)


async def check_sessions_without_code(proceedings_data: ProceedingsData) -> list[str]:
    """Detect sessions without a code that have contributions.

    The site has no page for a session without a code (see
    JACoW-org/MEOW#39): its contributions are not listed in any session page,
    so the editors are warned. Not blocking.
    """

    logger.info("event_final_proceedings - check_sessions_without_code")

    warnings: list[str] = []

    for session in proceedings_data.sessions:
        # same condition as HugoProceedingsPlugin.render_session
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
            f"has no code, so it has no page in the site and its contributions "
            f"are not listed in any session page: {', '.join(codes)}."
        )

    logger.warning(f"check_sessions_without_code: {len(warnings)} warning(s) found.")
    for w in warnings:
        logger.warning(w)

    return warnings
