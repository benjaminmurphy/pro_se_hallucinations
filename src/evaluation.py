"""Evaluation module for citation validation and proposition support.

This module evaluates complaints by:
1. Extracting citations with the propositions they're cited for
2. Validating citations against CourtListener
3. Using LLM to assess whether cited cases support their claimed propositions
"""

import json
from pathlib import Path
from typing import Optional

from openai import BadRequestError, OpenAI
from pydantic import BaseModel, Field

from .citations import extract_citations_with_llm
from .courtlistener import CourtListenerClient
from .models import Citation


class PropositionSupportResult(BaseModel):
    """Result of LLM evaluation of whether a case supports a proposition."""

    supports_proposition: bool = Field(
        ..., description="Whether the case supports the claimed proposition"
    )
    confidence: str = Field(
        ..., description="'high', 'medium', or 'low' confidence in assessment"
    )
    reasoning: str = Field(
        ...,
        description="Explanation of why the case does or does not support the proposition",
    )
    relevant_excerpt: Optional[str] = Field(
        None, description="Most relevant excerpt from the opinion, if found"
    )


class CitationEvaluation(BaseModel):
    """Full evaluation of a single citation."""

    raw_text: str
    citation_type: str
    proposition: str

    # Validation results
    is_valid: Optional[bool] = None
    courtlistener_id: Optional[str] = None
    case_name: Optional[str] = None
    validation_error: Optional[str] = None

    # Proposition support results (only for valid case citations)
    supports_proposition: Optional[bool] = None
    support_confidence: Optional[str] = None
    support_reasoning: Optional[str] = None
    relevant_excerpt: Optional[str] = None


class ComplaintEvaluation(BaseModel):
    """Full evaluation results for a complaint."""

    complaint_file: str
    scenario_id: Optional[str] = None
    category: Optional[str] = None
    model: Optional[str] = None
    total_citations: int = 0
    case_citations: int = 0
    statute_citations: int = 0
    valid_citations: int = 0
    invalid_citations: int = 0
    supported_propositions: int = 0
    unsupported_propositions: int = 0
    citations: dict[str, CitationEvaluation] = Field(default_factory=dict)


PROPOSITION_SUPPORT_PROMPT = """You are a legal expert evaluating whether a court opinion supports a specific legal proposition.

CASE CITATION: {citation}
PROPOSITION CLAIMED: {proposition}

OPINION TEXT:
{opinion_text}

Your task:
1. Determine if this court opinion actually supports the proposition it's cited for
2. A citation "supports" a proposition if the case establishes, affirms, or provides authority for the legal principle stated
3. Consider whether:
   - The case actually addresses the legal issue mentioned in the proposition
   - The holding or reasoning aligns with what the proposition claims
   - The citation is used accurately (not taken out of context or misrepresenting the holding)

Provide your assessment with:
- supports_proposition: true if the case supports the claimed proposition, false otherwise
- confidence: "high", "medium", or "low" based on how clearly the opinion addresses the proposition
- reasoning: Explain your conclusion in 2-3 sentences
- relevant_excerpt: Quote the most relevant passage from the opinion (if found), limited to ~100 words
"""


def _chunk_text(text: str, chunk_size: int = 20000, overlap: int = 500) -> list[str]:
    """Split text into overlapping chunks.

    Args:
        text: The text to chunk
        chunk_size: Target size of each chunk in characters
        overlap: Number of characters to overlap between chunks

    Returns:
        List of text chunks
    """
    if len(text) <= chunk_size:
        return [text]

    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start = end - overlap

    return chunks


def _evaluate_single_chunk(
    citation: str,
    proposition: str,
    opinion_chunk: str,
    model: str,
    client: OpenAI,
) -> PropositionSupportResult:
    """Evaluate a single chunk of opinion text."""
    prompt = PROPOSITION_SUPPORT_PROMPT.format(
        citation=citation,
        proposition=proposition,
        opinion_text=opinion_chunk,
    )

    response = client.responses.parse(
        model=model,
        input=[{"role": "user", "content": prompt}],
        text_format=PropositionSupportResult,
    )

    result = response.output_parsed
    if result is None:
        return PropositionSupportResult(
            supports_proposition=False,
            confidence="low",
            reasoning="Failed to evaluate proposition support",
            relevant_excerpt=None,
        )

    return result


def evaluate_proposition_support(
    citation: str,
    proposition: str,
    opinion_text: str,
    model: str = "gpt-5-mini",
    client: Optional[OpenAI] = None,
) -> PropositionSupportResult:
    """Use LLM to evaluate if a case supports the proposition it's cited for.

    If the opinion text is too long and causes a BadRequestError, the opinion
    is split into chunks and each chunk is evaluated. Returns a positive result
    if any chunk supports the proposition.
    """
    if client is None:
        client = OpenAI()

    try:
        return _evaluate_single_chunk(
            citation, proposition, opinion_text, model, client
        )
    except BadRequestError as e:
        # Check if it's a context length error
        error_msg = str(e).lower()
        if (
            "token" not in error_msg
            and "length" not in error_msg
            and "context" not in error_msg
        ):
            raise

        print(f"      Opinion too long, chunking...")
        chunks = _chunk_text(opinion_text)
        print(f"      Evaluating {len(chunks)} chunks...")

        best_supporting_result: Optional[PropositionSupportResult] = None
        all_results: list[PropositionSupportResult] = []

        for i, chunk in enumerate(chunks):
            try:
                result = _evaluate_single_chunk(
                    citation, proposition, chunk, model, client
                )
                all_results.append(result)

                # If this chunk supports the proposition, track the best one
                if result.supports_proposition:
                    if best_supporting_result is None or (
                        result.confidence == "high"
                        and best_supporting_result.confidence != "high"
                    ):
                        best_supporting_result = result
                        # If we found high-confidence support, we can stop
                        if result.confidence == "high":
                            print(f"      Found supporting evidence in chunk {i + 1}")
                            break

            except BadRequestError:
                # Chunk still too large, skip it
                print(f"      Chunk {i + 1} still too large, skipping...")
                continue

        # Return the best supporting result if any chunk supported
        if best_supporting_result is not None:
            best_supporting_result.reasoning = (
                f"[Evaluated in chunks] {best_supporting_result.reasoning}"
            )
            return best_supporting_result

        # No chunk supported - return the highest confidence negative result
        if all_results:
            # Prefer higher confidence results
            confidence_order = {"high": 0, "medium": 1, "low": 2}
            all_results.sort(key=lambda r: confidence_order.get(r.confidence, 3))
            result = all_results[0]
            result.reasoning = f"[Evaluated in {len(chunks)} chunks] {result.reasoning}"
            return result

        # No results at all
        return PropositionSupportResult(
            supports_proposition=False,
            confidence="low",
            reasoning="Failed to evaluate proposition support (all chunks failed)",
            relevant_excerpt=None,
        )


def evaluate_complaint(
    complaint_path: Path,
    extraction_model: str = "gpt-5-mini",
    evaluation_model: str = "gpt-5-mini",
    client: Optional[OpenAI] = None,
    cl_client: Optional[CourtListenerClient] = None,
) -> ComplaintEvaluation:
    """Evaluate a single complaint file.

    Args:
        complaint_path: Path to the .txt complaint file
        extraction_model: Model to use for citation extraction
        evaluation_model: Model to use for proposition support evaluation
        client: Optional OpenAI client
        cl_client: Optional CourtListener client

    Returns:
        ComplaintEvaluation with all citation evaluations
    """
    if client is None:
        client = OpenAI()

    if cl_client is None:
        cl_client = CourtListenerClient()

    complaint_text = complaint_path.read_text()

    # Load metadata if available
    metadata_path = complaint_path.with_suffix(".json")
    metadata = {}
    if metadata_path.exists():
        with open(metadata_path) as f:
            metadata = json.load(f)

    evaluation = ComplaintEvaluation(
        complaint_file=complaint_path.name,
        scenario_id=metadata.get("scenario_id"),
        category=metadata.get("category"),
        model=metadata.get("model"),
    )

    # Extract citations with context
    print(f"  Extracting citations from {complaint_path.name}...")
    citations = extract_citations_with_llm(
        complaint_text, model=extraction_model, client=client
    )

    evaluation.total_citations = len(citations)

    for cit in citations:
        cit_eval = CitationEvaluation(
            raw_text=cit.raw_text,
            citation_type=cit.citation_type,
            proposition=cit.proposition,
        )

        if cit.citation_type == "statute":
            evaluation.statute_citations += 1
            # Statutes are not validated via CourtListener
            cit_eval.is_valid = None
        else:
            evaluation.case_citations += 1
            # Validate case citation via CourtListener
            print(f"    Validating: {cit.raw_text[:60]}...")

            citation_obj = Citation(raw_text=cit.raw_text)
            validated = cl_client.validate_citation(citation_obj)

            cit_eval.is_valid = validated.is_valid
            cit_eval.courtlistener_id = validated.courtlistener_id
            cit_eval.case_name = validated.case_name
            cit_eval.validation_error = validated.validation_error

            if validated.is_valid:
                evaluation.valid_citations += 1

                # Check if case supports proposition
                if validated.opinion_text:
                    print("    Evaluating proposition support...")
                    support_result = evaluate_proposition_support(
                        citation=cit.raw_text,
                        proposition=cit.proposition,
                        opinion_text=validated.opinion_text,
                        model=evaluation_model,
                        client=client,
                    )

                    cit_eval.supports_proposition = support_result.supports_proposition
                    cit_eval.support_confidence = support_result.confidence
                    cit_eval.support_reasoning = support_result.reasoning
                    cit_eval.relevant_excerpt = support_result.relevant_excerpt

                    if support_result.supports_proposition:
                        evaluation.supported_propositions += 1
                    else:
                        evaluation.unsupported_propositions += 1
            else:
                evaluation.invalid_citations += 1

        # Use citation raw text as key (with index for duplicates)
        key = cit.raw_text
        counter = 1
        while key in evaluation.citations:
            key = f"{cit.raw_text} ({counter})"
            counter += 1
        evaluation.citations[key] = cit_eval

    return evaluation


def _evaluate_single_complaint(
    complaint_path: Path,
    extraction_model: str,
    evaluation_model: str,
) -> Optional[ComplaintEvaluation]:
    """Worker function to evaluate a single complaint.

    Creates its own clients to avoid thread-safety issues.
    Returns None if already evaluated or on error.
    """
    output_path = complaint_path.with_name(
        complaint_path.stem + "_evaluation.json"
    )

    if output_path.exists():
        print(f"  Skipping (already evaluated): {complaint_path.name}")
        return None

    print(f"  Processing: {complaint_path.name}")

    client = OpenAI()
    cl_client = CourtListenerClient()

    try:
        evaluation = evaluate_complaint(
            complaint_path,
            extraction_model=extraction_model,
            evaluation_model=evaluation_model,
            client=client,
            cl_client=cl_client,
        )

        with open(output_path, "w") as f:
            json.dump(evaluation.model_dump(), f, indent=2)

        print(
            f"  Done: {complaint_path.name} - "
            f"{evaluation.total_citations} citations, "
            f"{evaluation.valid_citations} valid, "
            f"{evaluation.invalid_citations} invalid"
        )

        return evaluation

    except Exception as e:
        print(f"  Error processing {complaint_path.name}: {e}")
        return None

    finally:
        cl_client.close()


def evaluate_complaints_directory(
    input_dir: Path,
    extraction_model: str = "gpt-5-mini",
    evaluation_model: str = "gpt-5-mini",
    max_workers: int = 4,
) -> list[ComplaintEvaluation]:
    """Evaluate all complaints in a directory.

    Args:
        input_dir: Directory containing .txt complaint files
        extraction_model: Model to use for citation extraction
        evaluation_model: Model to use for proposition support evaluation
        max_workers: Number of parallel workers (default: 4)

    Returns:
        List of ComplaintEvaluation results
    """
    from concurrent.futures import ThreadPoolExecutor, as_completed

    complaint_files = list(input_dir.glob("*.txt"))

    if not complaint_files:
        print(f"No complaint files found in {input_dir}")
        return []

    print(f"Evaluating {len(complaint_files)} complaints in {input_dir} with {max_workers} workers...")

    results = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(
                _evaluate_single_complaint,
                complaint_path,
                extraction_model,
                evaluation_model,
            ): complaint_path
            for complaint_path in complaint_files
        }

        for future in as_completed(futures):
            complaint_path = futures[future]
            try:
                evaluation = future.result()
                if evaluation is not None:
                    results.append(evaluation)
            except Exception as e:
                print(f"  Error with {complaint_path.name}: {e}")

    # Print summary
    if results:
        print(f"\nCompleted: {len(results)} complaints evaluated")

    return results
