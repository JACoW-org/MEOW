import logging as lg
from typing import Any

from meow.models.local.event.final_proceedings.proceedings_data_model import ProceedingsData


logger = lg.getLogger(__name__)


async def validate_proceedings_data(proceedings_data: ProceedingsData, cookies: dict, settings: dict, callback: Any) -> list:
    """ """

    logger.info('event_final_proceedings - validate_events_data')

    pdf_page_width: float = float(settings.get('pdf_page_width', 0))
    pdf_page_height: float = float(settings.get('pdf_page_height', 0))

    logger.error(pdf_page_width)
    logger.error(pdf_page_height)

    metadata: list = []
    errors: list = []
    
    total_count: int = 0
    qa_approved_count: int = 0
    qa_pending_count: int = 0

    for contribution_data in proceedings_data.contributions:
        if contribution_data.code and contribution_data.metadata:

            if callback(contribution_data):
                
                total_count += 1
                
                if contribution_data.is_qa_approved:
                    qa_approved_count += 1
                    
                if contribution_data.is_qa_pending:
                    qa_pending_count += 1                

                metadata.append(contribution_data.metadata)

                error: dict = dict()

                # {
                # 'page_count': 1,
                # 'pages_report': [{'sizes': {'width': 792.0, 'height': 595.0}}],
                # 'fonts_report': [{'name': 'CSKTLK+LMRoman10-Regular', 'emb': True, 'ext': 'cff', 'type': 'Type1'}]
                # }

                page_count: int = contribution_data.metadata.get(
                    'page_count', 0)
                
                if page_count == 0:
                    
                    error['page_size'] = False
                    error['font_emb'] = False
                    
                else:
                
                    pages_report: list[dict] = contribution_data.metadata.get(
                        'pages_report', [])
                    
                    fonts_report: list[dict] = contribution_data.metadata.get(
                        'fonts_report', [])
                    
                    for page_report in pages_report:
                        page_sizes = page_report.get('sizes', {})
                        page_width: float = float(page_sizes.get('width', 0.0))
                        page_height: float = float(page_sizes.get('height', 0.0))

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
    logger.info(f"total_count: {total_count}")
    logger.info(f"qa_approved_count: {qa_approved_count}")
    logger.info(f"qa_pending_count: {qa_pending_count}")
    logger.info(f"####################")
    logger.info(f"")

    return [metadata, errors]
