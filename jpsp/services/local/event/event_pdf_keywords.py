import logging as lg

from fitz import Document

from typing import AsyncGenerator
from io import StringIO, open

from anyio import Path, create_task_group, CapacityLimiter, to_process, to_thread
from anyio import create_memory_object_stream, ClosedResourceError

from anyio.streams.memory import MemoryObjectSendStream
from jpsp.services.local.event.event_pdf_utils import is_to_download

from jpsp.utils.http import download_file

from nltk.tokenize import wordpunct_tokenize
from nltk.stem.snowball import SnowballStemmer

from jpsp.utils import keywords


logger = lg.getLogger(__name__)


async def event_pdf_keywords(event: dict, cookies: dict, settings: dict) -> AsyncGenerator:
    """ """

    # logger.debug(f'event_pdf_download - count: {len(contributions)} - cookies: {cookies}')

    stemmer = SnowballStemmer("english")

    # stem default keywords
    stem_keywords_dict = stem_keywords_as_tree(keywords.KEYWORDS, stemmer)

    event_id = event.get('id', 'event')

    pdf_cache_dir: Path = Path('var', 'run', f"{event_id}_pdf")
    await pdf_cache_dir.mkdir(exist_ok=True, parents=True)

    contributions: list[dict] = event.get("contributions", list())

    files = await extract_event_pdf_files(contributions)

    total_files: int = len(files)
    checked_files: int = 0

    # logger.debug(f'event_pdf_check - files: {len(files)}')

    send_stream, receive_stream = create_memory_object_stream()

    capacity_limiter = CapacityLimiter(4)

    async with create_task_group() as tg:
        async with send_stream:
            for current_index, current_file in enumerate(files):
                tg.start_soon(pdf_keywords_task, capacity_limiter, total_files,
                              current_index, current_file, cookies, pdf_cache_dir,
                              stemmer, stem_keywords_dict, send_stream.clone())

        try:
            async with receive_stream:
                async for report in receive_stream:
                    checked_files = checked_files + 1
                    
                    # print('receive_reports_stream::report-->',
                    #       checked_files, total_files, report)

                    yield dict(
                        type='progress',
                        value=report
                    )

                    if checked_files >= total_files:
                        receive_stream.close()

                        yield dict(
                            type='final',
                            value=None
                        )

        except ClosedResourceError:
            pass


async def extract_event_pdf_files(elements: list[dict]) -> list:
    """ """

    files = []

    for element in elements:
        revisions = element.get('revisions', [])
        for file in revisions[-1].get('files', []):
            files.append(file)

        # for revision in element.get('revisions', []):
        #     for file in revision.get('files', []):
        #         files.append(file)

    return files


async def pdf_keywords_task(capacity_limiter: CapacityLimiter, total_files: int, current_index: int, current_file: dict, cookies: dict, pdf_cache_dir: Path, stemmer: SnowballStemmer, stem_keywords_dict: dict[str, list[str]], res: MemoryObjectSendStream) -> None:
    """ """

    async with capacity_limiter:
        keywords = await internal_pdf_keywords_task(current_file, cookies, pdf_cache_dir, stemmer, stem_keywords_dict)

        await res.send({
            "index": current_index,
            "total": total_files,
            "file": current_file,
            "keywords": keywords
        })


async def internal_pdf_keywords_task(current_file: dict, cookies: dict, pdf_cache_dir: Path, stemmer: SnowballStemmer,
               stem_keywords_dict: dict[str, list[str]]) -> list[str]:
    """ """

    pdf_md5 = current_file.get('md5sum', '')
    pdf_name = current_file.get('filename', '')
    http_sess = cookies.get('indico_session_http', '')
    pdf_url = current_file.get('external_download_url', '')

    pdf_file = Path(pdf_cache_dir, pdf_name)

    print([pdf_md5, pdf_name])

    if await is_to_download(pdf_file, pdf_md5):
        cookies = dict(indico_session_http=http_sess)
        await download_file(url=pdf_url, file=pdf_file, cookies=cookies)

    # IN PROCESS
    # paper_keywords = get_keywords_from_text(str(await pdf_file.absolute()), stemmer, stem_keywords_dict)
    
    # EXTERNAL THREAD
    # paper_keywords = await to_thread.run_sync(get_keywords_from_pdf, str(await pdf_file.absolute()), stemmer, stem_keywords_dict)
    
    # EXTERNAL PROCESS
    paper_keywords = await to_process.run_sync(get_keywords_from_pdf, str(await pdf_file.absolute()), stemmer, stem_keywords_dict)

    return paper_keywords


def get_keywords_from_pdf(path: str, stemmer: SnowballStemmer, stem_keywords_dict: dict[str, list[str]]) -> list[str]:

    with open(path, 'rb') as fh:

        txt = pdf_to_txt(fh.read())

        pdf_keywords = get_keywords_from_text(txt, stemmer, stem_keywords_dict)

        return pdf_keywords


def pdf_to_txt(stream: bytes) -> str:
    """ """

    out = StringIO()
    
    try:

        doc = Document(stream=stream, filetype='pdf')
        
        try:
            
            for page in doc:  # iterate the document pages
                text = page.get_textpage().extractText()  # get plain text (is in UTF-8)
                out.write(text)  # write text of page
                    
        except Exception as e:
            logger.error(e, exc_info=True)
            
        doc.close()
                  
    except Exception as e:
        logger.error(e, exc_info=True)

    return out.getvalue()


def sort_coo(coo_matrix):
    tuples = zip(coo_matrix.col, coo_matrix.data)
    return sorted(tuples, key=lambda x: (x[1], x[0]), reverse=True)


def extract_topn_from_vector(feature_names, sorted_items, topn=10) -> dict:

    sorted_items = sorted_items[:topn]

    score_vals = []
    feature_vals = []
    for idx, score in sorted_items:
        score_vals.append(round(score, 3))
        feature_vals.append(feature_names[idx])

    results = {}
    for idx in range(len(feature_vals)):
        results[feature_vals[idx]] = score_vals[idx]

    return results


def stem_keywords_greedy(keywords: list[str], stemmer: SnowballStemmer) -> dict[str, str]:

    keywords_stems = {}

    for keyword in keywords:
        keywords_stems[stemmer.stem(wordpunct_tokenize(keyword)[0])] = keyword

    return keywords_stems


def stem_keywords_as_tree(keywords: list[str], stemmer: SnowballStemmer) -> dict[str, list[str]]:

    keywords_stems_tree: dict[str, list[str]] = {}

    for keyword in keywords:
        # TODO use different tokenization method to improve
        keyword_tokens = wordpunct_tokenize(keyword)
        first_token_stem = stemmer.stem(keyword_tokens[0])
        if first_token_stem in keywords_stems_tree:
            keywords_stems_tree[first_token_stem].append(keyword)
        else:
            keywords_stems_tree[first_token_stem] = [keyword]

    return keywords_stems_tree


def get_keywords_from_text_greedy(text: str, stemmer: SnowballStemmer, stem_keywords: dict) -> list[str]:

    text_tokens = wordpunct_tokenize(text)

    text_keywords_counts: dict[str, int] = {}
    for token in text_tokens:
        token_stem = stemmer.stem(token)
        if token_stem in stem_keywords:
            keyword = stem_keywords[token_stem]
            if keyword in text_keywords_counts:
                text_keywords_counts[keyword] += 1
            else:
                text_keywords_counts[keyword] = 1

    return get_top_keywords(text_keywords_counts)


def get_keywords_from_text(text: str, stemmer: SnowballStemmer, stem_keywords_tree: dict[str, list[str]]) -> list[str]:

    text_tokens: list[str] = wordpunct_tokenize(text)

    # init keywords counts
    text_keywords_counts: dict[str, int] = {}
    # O(n)
    # for i in range(len(text_tokens)):
    for i, token in enumerate(text_tokens):

        # token: str = text_tokens[i]
        if stemmer.stem(token) in stem_keywords_tree:

            token_stem: str = stemmer.stem(token)
            # O(m), m is the amount of keywords in the list with the same stem
            for keyword in stem_keywords_tree[token_stem]:

                # TODO use different tokenization method to improve
                keyword_tokens: list[str] = wordpunct_tokenize(keyword)
                j: int = 1
                isMatch: bool = True
                keyword_tokens_len: int = len(keyword_tokens)
                # O(k), where k is usually ~1/2
                while (isMatch and j < keyword_tokens_len):
                    isMatch = keyword_tokens[j] == text_tokens[i + j]
                    j += 1

                if isMatch:
                    if keyword in text_keywords_counts:
                        text_keywords_counts[keyword] += 1
                    else:
                        text_keywords_counts[keyword] = 1

    return get_top_keywords(text_keywords_counts)


def get_top_keywords(candidates: dict[str, int]) -> list[str]:

    sorted_candidates = sorted(
        candidates.items(), key=lambda x: x[1], reverse=True)

    top_keywords = []
    index = 0
    while (index < len(sorted_candidates) and (index < 5 or sorted_candidates[index][1] == sorted_candidates[index - 1][1])):
        top_keywords.append(sorted_candidates[index][0])
        index += 1

    return top_keywords


def get_keywords(vectorizer, features, report) -> dict[str, list[str]]:

    tf_idf_vector = vectorizer.transform([report.get('txt')])

    sorted_items = sort_coo(tf_idf_vector.tocoo())

    keywords = extract_topn_from_vector(features, sorted_items, 10)

    return dict(
        file=report.get('file'),
        keywords=list(keywords.keys())
    )


def get_paper_keywords_by_stem(paper_tokens: list, stemmer: SnowballStemmer, keywords_stems_map: dict) -> list:

    # get occurences of all keywords given in input for the this paper
    paper_keywords = {}
    for token in paper_tokens:
        stem = stemmer.stem(token)
        if stem in keywords_stems_map:
            keyword = keywords_stems_map[stem]
            if keyword in paper_keywords:
                paper_keywords[keyword] += 1
            else:
                paper_keywords[keyword] = 1

    # filter keywords
    sorted_paper_keywords = sorted(
        paper_keywords.items(), key=lambda x: x[1], reverse=True)

    filtered_paper_keywords = []

    index = 0
    while (index < 5 or sorted_paper_keywords[index][1] == sorted_paper_keywords[index - 1][1]):
        filtered_paper_keywords.append(sorted_paper_keywords[index][0])
        index += 1

    return filtered_paper_keywords
