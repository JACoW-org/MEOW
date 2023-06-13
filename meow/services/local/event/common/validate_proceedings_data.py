import logging as lg
from typing import Callable

from meow.models.local.event.final_proceedings.proceedings_data_model import ProceedingsData


logger = lg.getLogger(__name__)


async def validate_proceedings_data(proceedings_data: ProceedingsData, cookies: dict, settings: dict, callback: Callable) -> list:
    """ """

    logger.info('event_final_proceedings - validate_events_data')

    pdf_page_width: float = float(settings.get('pdf_page_width', 0))
    pdf_page_height: float = float(settings.get('pdf_page_height', 0))

    logger.error(pdf_page_width)
    logger.error(pdf_page_height)

    metadatas: list[dict] = []
    errors: list[dict] = []

    total_count: list[str] = []

    included_in_proceedings: list[str] = []
    included_in_prepress: list[str] = []
    included_in_check: list[str] = []

    for contribution_data in proceedings_data.contributions:

        if contribution_data.code and contribution_data.metadata:

            metadata: dict = contribution_data.metadata

            total_count.append(contribution_data.code)

            if callback(contribution_data):

                if contribution_data.is_included_in_proceedings:
                    included_in_proceedings.append(contribution_data.code)
                    
                if contribution_data.is_included_in_prepress:
                    included_in_prepress.append(contribution_data.code)
                    
                if contribution_data.is_included_in_pdf_check:
                    included_in_check.append(contribution_data.code)
                    
                metadatas.append(metadata)

                error: dict = {}

                pages_report: list[dict] = []
                fonts_report: list[dict] = []

                # {
                # 'page_count': 1,
                # 'pages_report': [{'sizes': {'width': 792.0, 'height': 595.0}}],
                # 'fonts_report': [{'name': 'CSKTLK+LMRoman10-Regular', 'emb': True, 'ext': 'cff', 'type': 'Type1'}]
                # }

                page_count: int = metadata.get('page_count', 0)
                pages_report = metadata.get('pages_report', [])
                fonts_report = metadata.get('fonts_report', [])

                if page_count == 0:

                    error['page_size'] = False
                    error['font_emb'] = False

                else:

                    for page_report in pages_report:

                        page_sizes = page_report.get('sizes', {})
                        page_width = float(page_sizes.get('width', 0.0))
                        page_height = float(page_sizes.get('height', 0.0))

                        if float(page_width) != pdf_page_width or page_height != pdf_page_height:

                            logger.info(f"code: {contribution_data.code}")
                            logger.info({'page_width': page_width, 'pdf_page_width': pdf_page_width,
                                        'page_height': page_height, 'pdf_page_height': pdf_page_height})

                            error['page_size'] = False
                            break

                    for font_report in fonts_report:
                        font_emb: bool = bool(font_report.get('emb', False))
                        
                        if font_emb == False:

                            logger.info(f"code: {contribution_data.code}")
                            logger.info(fonts_report)

                            error['font_emb'] = False
                            break

                if len(error.keys()) > 0:
                    errors.append({
                        **error,
                        'url': contribution_data.url,
                        'code': contribution_data.code,
                        'title': contribution_data.title,
                    })

    logger.info(f"")
    logger.info(f"####################")
    logger.info(f"total_count: {len(total_count)}")
    logger.info(f"included_in_proceedings: {len(included_in_proceedings)}")
    logger.info(f"included_in_prepress: {len(included_in_prepress)}")
    logger.info(f"included_in_check: {len(included_in_check)}")
    logger.info(f"####################")
    logger.info(f"")

    return [metadatas, errors]
