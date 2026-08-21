from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request

from src.llm.analyzer import TestLogAnalyzer
from src.llm.response_generator import ResponseGenerator
from src.retrieval.hybrid_search import HybridSearch
from src.retrieval.query_builder import build_search_query


BASE_DIR = Path(__file__).resolve().parent

templates = Jinja2Templates(
    directory=str(
        BASE_DIR / "templates"
    )
)


app = FastAPI(
    title="AI Test Failure Analysis Agent",
    description=(
        "AI-assisted historical test failure analysis"
    ),
    version="0.1.0",
)


def analyze_log(test_log: str):

    # ------------------------------------------
    # Step 1: Analyze log
    # ------------------------------------------

    analyzer = TestLogAnalyzer()

    analysis = analyzer.analyze(
        test_log
    )

    # ------------------------------------------
    # Step 2: Build search query
    # ------------------------------------------

    search_query = build_search_query(
        analysis
    )

    # ------------------------------------------
    # Step 3: Hybrid search
    # ------------------------------------------

    hybrid_search = HybridSearch()

    ranked_results = hybrid_search.search(
        analysis,
        top_k=5,
    )

    # ------------------------------------------
    # Prepare evidence
    # ------------------------------------------

    search_results = {

        "ids": [
            [
                r["id"]
                for r in ranked_results
            ]
        ],

        "documents": [
            [
                r["document"]
                for r in ranked_results
            ]
        ],

        "metadatas": [
            [
                {
                    "source": r["source"],
                    "title": r["title"],
                    "component": r["component"],
                    "affected_software_version": (
                        r[
                            "affected_software_version"
                        ]
                    ),
                    "fix_software_version": (
                        r[
                            "fix_software_version"
                        ]
                    ),
                }
                for r in ranked_results
            ]
        ],

        "distances": [
            [
                r["distance"]
                for r in ranked_results
            ]
        ],
    }

    # ------------------------------------------
    # Step 4: Generate analysis
    # ------------------------------------------

    generator = ResponseGenerator()

    final_analysis = generator.generate(
        test_log=test_log,
        analysis=analysis,
        search_results=search_results,
    )

    return {
        "analysis": analysis,
        "search_query": search_query,
        "historical_records": ranked_results,
        "final_analysis": final_analysis,
    }


@app.get(
    "/",
    response_class=HTMLResponse,
)
async def home(
    request: Request,
):

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
        },
    )


@app.post(
    "/analyze",
    response_class=HTMLResponse,
)
async def analyze(
    request: Request,
    log_text: str = Form(""),
    log_file: Optional[UploadFile] = File(None),
):

    # ------------------------------------------
    # Determine input
    # ------------------------------------------

    test_log = log_text.strip()

    if (
        not test_log
        and log_file
        and log_file.filename
    ):

        content = await log_file.read()

        test_log = content.decode(
            "utf-8",
            errors="replace",
        )

    if not test_log:

        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "error": (
                    "Please paste a log or "
                    "upload a log file."
                ),
            },
        )

    # ------------------------------------------
    # Run analysis
    # ------------------------------------------

    result = analyze_log(
        test_log
    )

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "test_log": test_log,
            "analysis": result["analysis"],
            "search_query": result[
                "search_query"
            ],
            "historical_records": result[
                "historical_records"
            ],
            "final_analysis": result[
                "final_analysis"
            ],
        },
    )