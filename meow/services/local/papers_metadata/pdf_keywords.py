import logging as lg

from fitz import Document

from nltk.tokenize import wordpunct_tokenize
from nltk.stem.snowball import SnowballStemmer

from meow.services.local.papers_metadata.pdf_to_txt import pdf_to_txt


logger = lg.getLogger(__name__)


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


def get_keywords_from_text(pdf: Document, stemmer: SnowballStemmer, stem_keywords_tree: dict[str, list[str]]) -> list[str]:
    
    text = pdf_to_txt(pdf)

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
