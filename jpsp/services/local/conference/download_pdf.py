
from io import StringIO
import logging as lg
import hashlib as hl

import nltk

from anyio import Path, create_task_group, CapacityLimiter
from anyio import create_memory_object_stream, ClosedResourceError

from anyio.streams.memory import MemoryObjectSendStream


from jpsp.utils.http import download_file

from nltk.tokenize import wordpunct_tokenize
from nltk.stem.snowball import SnowballStemmer

from jpsp.utils import keywords

nltk.download('punkt')
nltk.download('stopwords')


logger = lg.getLogger(__name__)


async def event_pdf_download(event: dict, cookies: dict, settings: dict):
    """ """

    # logger.debug(f'event_pdf_download - count: {len(contributions)} - cookies: {cookies}')

    event_id = event.get('id', 'event')

    pdf_dir: Path = Path('var', 'run', f"{event_id}_pdf")
    await pdf_dir.mkdir(exist_ok=True, parents=True)

    contributions: list[dict] = event.get("contributions", list())

    files = await extract_event_pdf_files(contributions)

    total_files: int = len(files)
    checked_files: int = 0

    # logger.debug(f'event_pdf_check - files: {len(files)}')

    send_reports_stream, receive_reports_stream = create_memory_object_stream()

    limiter = CapacityLimiter(6)

    async with create_task_group() as tg:
        async with send_reports_stream:
            for index, current in enumerate(files):
                tg.start_soon(_task, limiter, total_files, 
                              index, current, cookies, pdf_dir, 
                              send_reports_stream.clone())

        stemmer = SnowballStemmer("english")
        result = []

        # stem default keywords
        stem_keywords_dict = stem_keywords_as_tree(keywords.KEYWORDS, stemmer)

        try:
            async with receive_reports_stream:
                async for report in receive_reports_stream:
                    checked_files = checked_files + 1

                    paper_keywords = get_keywords_from_text(report.get('txt'), stemmer, stem_keywords_dict)

                    result.append(dict(
                        file=report.get('file'),
                        keywords=paper_keywords
                    ))

                    logger.debug(f'keyword count for report {report.get("file").get("filename")}: {paper_keywords}')

                    yield dict(
                        type='progress',
                        value=report
                    )

                    if checked_files >= total_files:

                        yield dict(
                            type='final',
                            value=result
                        )

                        receive_reports_stream.close()

        except ClosedResourceError:
            pass

def sort_coo(coo_matrix):
    tuples = zip(coo_matrix.col, coo_matrix.data)
    return sorted(tuples, key=lambda x: (x[1], x[0]), reverse=True)


def extract_topn_from_vector(feature_names, sorted_items, topn=10):
    
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

def stem_keywords_greedy(keywords: list[str], stemmer: SnowballStemmer) -> dict[str]:

    keywords_stems = {}

    for keyword in keywords:
        keywords_stems[stemmer.stem(wordpunct_tokenize(keyword)[0])] = keyword

    return keywords_stems

def stem_keywords_as_tree(keywords: list[str], stemmer: SnowballStemmer) -> dict[list[str]]:

    keywords_stems_tree: dict[list[str]] = {}

    for keyword in keywords:
        # TODO use different tokenization method to improve
        keyword_tokens = wordpunct_tokenize(keyword)
        first_token_stem = stemmer.stem(keyword_tokens[0])
        if first_token_stem in keywords_stems_tree:
            keywords_stems_tree[first_token_stem].append(keyword)
        else:
            keywords_stems_tree[first_token_stem] = [keyword]

    return keywords_stems_tree

def get_keywords_from_text_greedy(text: str, stemmer: SnowballStemmer, stem_keywords: dict[str]) -> list[str]:

    text_tokens = wordpunct_tokenize(text)
    
    text_keywords_counts: dict[int] = {}
    for token in text_tokens:
        token_stem = stemmer.stem(token)
        if token_stem in stem_keywords:
            keyword = stem_keywords[token_stem]
            if keyword in text_keywords_counts:
                text_keywords_counts[keyword] += 1
            else:
                text_keywords_counts[keyword] = 1

    return get_top_keywords(text_keywords_counts)

def get_keywords_from_text(text: str, stemmer: SnowballStemmer, stem_keywords_tree: dict[list[str]]) -> list[str]:

    text_tokens: list[str] = wordpunct_tokenize(text)

    # init keywords counts
    text_keywords_counts: dict[int] = {}
    # O(n)
    for i in range(len(text_tokens)):
        
        token: str = text_tokens[i]
        if stemmer.stem(token) in stem_keywords_tree:

            token_stem: str = stemmer.stem(token)
            # O(m), m is the amount of keywords in the list with the same stem
            for keyword in stem_keywords_tree[token_stem]:
                
                keyword_tokens: list[str] = wordpunct_tokenize(keyword)
                j: int = 1
                isMatch: bool = True
                # O(k), where k is usually ~1/2
                while (isMatch and j < len(keyword_tokens)):
                    isMatch = keyword_tokens[j] == text_tokens[i + j]
                    j += 1

                if isMatch:
                    if keyword in text_keywords_counts:
                        text_keywords_counts[keyword] += 1
                    else:
                        text_keywords_counts[keyword] = 1

    return get_top_keywords(text_keywords_counts)

def get_top_keywords(candidates: dict[int]) -> list[str]:

    sorted_candidates = sorted(candidates.items(), key=lambda x:x[1], reverse=True)

    top_keywords = []
    index = 0
    while (index < len(sorted_candidates) and (index < 5 or sorted_candidates[index][1] == sorted_candidates[index - 1][1])):
        top_keywords.append(sorted_candidates[index][0])
        index += 1

    return top_keywords

def get_keywords(vectorizer, features, report):

    tf_idf_vector = vectorizer.transform([report.get('txt')])

    sorted_items = sort_coo(tf_idf_vector.tocoo())

    keywords = extract_topn_from_vector(features, sorted_items, 10)

    return dict(
        file=report.get('file'),
        keywords=list(keywords.keys())
    )


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


async def _task(l: CapacityLimiter, t: int, i: int, f: dict, c: dict, p: Path, res: MemoryObjectSendStream):
    """ """

    async with l:
        r = await _run(f, c, p)

        await res.send({
            "index": i,
            "total": t,
            "file": f,
            "txt": r
        })


async def _run(f: dict, c: dict, p: Path):
    """ """

    md5 = f.get('md5sum', '')
    name = f.get('filename', '')
    sess = c.get('indico_session_http', '')
    url = f.get('external_download_url', '')

    file = Path(p, name)

    print([md5, name])

    if await _is_to_download(file, md5):
        cookies = dict(indico_session_http=sess)
        await download_file(url=url, file=file, cookies=cookies)

    txt = pdf_to_txt(await file.read_bytes())

    return txt


def pdf_to_txt(stream: bytes) -> str:
    """ """

    # non è oneroso importare fitz n volte ?
    from fitz import Document

    out = StringIO()

    doc = Document(stream=stream, filetype='pdf')

    for page in doc:  # iterate the document pages
        text = page.get_textpage().extractText()  # get plain text (is in UTF-8)
        out.write(text)  # write text of page

    return out.getvalue()

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
    sorted_paper_keywords = sorted(paper_keywords.items(), key=lambda x:x[1], reverse=True)

    filtered_paper_keywords = []

    index = 0
    while (index < 5 or sorted_paper_keywords[index][1] == sorted_paper_keywords[index - 1][1]):
        filtered_paper_keywords.append(sorted_paper_keywords[index][0])
        index += 1

    return filtered_paper_keywords

async def _is_to_download(f: Path, m: str) -> bool:
    """ """

    e = await f.exists()

    d = m == '' or e == False or m != await _md5(f, m)

    if d == True:
        print(await f.absolute(), '-->', 'download')
    else:
        print(await f.absolute(), '-->', 'skip')

    return d


async def _md5(f: Path, m: str) -> str:

    h = hl.md5(await f.read_bytes()).hexdigest()

    # print(await f.absolute(), m, h)

    return h
