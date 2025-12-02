"""Citation extraction from legal complaints using LLM.

This module extracts legal citations from complaint text using an LLM,
which provides more robust extraction than regex patterns for the
varied citation formats found in pro se filings.
"""

from typing import Optional

from openai import OpenAI
from pydantic import BaseModel, Field


class ExtractedCitation(BaseModel):
    """Schema for LLM-extracted citation."""

    raw_text: str
    citation_type: str  # "case" or "statute"
    proposition: str = Field(
        "", description="The sentence or claim the citation supports"
    )


class CitationExtractionResult(BaseModel):
    """Schema for LLM citation extraction response."""

    citations: list[ExtractedCitation]


EXTRACTION_PROMPT = """You are a legal citation extraction system. Your task is to identify all legal citations from the provided complaint text AND the specific proposition or legal claim each citation is used to support.

Extract two types of citations:
1. Case citations (e.g., "Smith v. Jones, 123 F.3d 456 (1st Cir. 2020)")
2. Statutory citations (e.g., "42 U.S.C. § 1983", "M.G.L. c. 93A, § 2", "G.L. c. 231, § 85")

For each citation, extract:
- raw_text: The citation exactly as it appears in the text
- citation_type: Either "case" or "statute"
- proposition: The complete sentence or legal claim that the citation is supporting. This should be the actual text from the complaint that precedes or follows the citation and states what legal principle or fact the citation is meant to establish.

Important:
- For inline citations like "_See Smith v. Jones,_ 123 F.3d 456", the proposition is the sentence containing or preceding the citation
- Include the full proposition text, not just a summary
- Each citation should appear only once, even if repeated in the document

Here is the complaint text:

"""


def extract_citations_with_llm(
    text: str, model: str = "gpt-5-mini", client: Optional[OpenAI] = None
) -> list[ExtractedCitation]:
    """Extract citations from text using an LLM.

    Args:
        text: The legal document text to extract citations from
        model: The OpenAI model to use for extraction
        client: Optional pre-configured OpenAI client

    Returns:
        List of Citation objects with extracted information
    """
    if client is None:
        client = OpenAI()

    response = client.responses.parse(
        model=model,
        input=[{"role": "user", "content": EXTRACTION_PROMPT + text}],
        text_format=CitationExtractionResult,
    )

    result = response.output_parsed
    if result is None:
        return []

    return result.citations
