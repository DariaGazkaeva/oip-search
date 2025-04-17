from typing import Optional

import numpy as np
from fastapi import FastAPI, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from vector_search import (
    load_index,
    load_tfidf,
    get_similar_documents,
    parse_search_query,
)


app = FastAPI()


index_file = "../task_1/results/index.txt"
tfidf_dir = "../task_4/results"
index = load_index(index_file)
vectors, lemma_idf, all_lemmas = load_tfidf(tfidf_dir)
document_ids = np.array(list(vectors.keys()))

templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def read_root(
    request: Request,
    search_query: Optional[str] = Query(None),
    page: int = Query(1, gt=0),
    number_results: int = Query(10, gt=0, le=50),
):
    document_urls = []
    similarity = []
    total_results = 0

    if search_query:
        query_vector = parse_search_query(search_query, all_lemmas, lemma_idf)

        sorted_document_ids, similarity = get_similar_documents(
            query_vector, vectors, document_ids
        )

        # Пагинация
        start_index = (page - 1) * number_results
        end_index = start_index + number_results

        total_results = len(similarity)
        document_urls = [
            index[doc_id] for doc_id in sorted_document_ids[start_index:end_index]
        ]
        similarity = similarity[start_index:end_index].tolist()
        similarity = [round(sim, 5) for sim in similarity]

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "document_urls": document_urls,
            "similarity": similarity,
            "search_query": search_query,
            "page": page,
            "number_results": number_results,
            "total_results": total_results,
        },
    )
