"""Seek hybrid search — vector + FTS5 with RRF fusion."""

from .store import search_vector, search_fts


def hybrid_search(conn, query, query_embedding, top_k=5, mode="hybrid", label=None):
    """Run search and return merged results.
    Returns list of dicts: {source_path, label, chunk_text, line_start, line_end, score, match_type}
    """
    results = {}

    if mode in ("semantic", "hybrid") and query_embedding is not None:
        vec_results = search_vector(conn, query_embedding, top_k=top_k * 2, label=label)
        for rank, (score, row) in enumerate(vec_results):
            key = (row["source_path"], row["line_start"])
            if key not in results:
                results[key] = {
                    "source_path": row["source_path"],
                    "label": row["label"],
                    "chunk_text": row["chunk_text"],
                    "line_start": row["line_start"],
                    "line_end": row["line_end"],
                    "rrf_score": 0.0,
                    "match_type": set(),
                    "raw_semantic": score,
                }
            results[key]["rrf_score"] += 1.0 / (60 + rank + 1)
            results[key]["match_type"].add("semantic")

    if mode in ("exact", "hybrid"):
        fts_results = search_fts(conn, query, top_k=top_k * 2, label=label)
        for rank, (score, row) in enumerate(fts_results):
            key = (row["source_path"], row["line_start"])
            if key not in results:
                results[key] = {
                    "source_path": row["source_path"],
                    "label": row["label"],
                    "chunk_text": row["chunk_text"],
                    "line_start": row["line_start"],
                    "line_end": row["line_end"],
                    "rrf_score": 0.0,
                    "match_type": set(),
                    "raw_semantic": 0.0,
                }
            results[key]["rrf_score"] += 1.0 / (60 + rank + 1)
            results[key]["match_type"].add("exact")

    # Sort by RRF score, use raw semantic as tiebreaker
    sorted_results = sorted(results.values(), key=lambda x: (-x["rrf_score"], -x.get("raw_semantic", 0)))

    # Normalize scores to 0-1 range for display
    if sorted_results:
        max_score = sorted_results[0]["rrf_score"]
        if max_score > 0:
            for r in sorted_results:
                r["score"] = r["rrf_score"] / max_score
        else:
            for r in sorted_results:
                r["score"] = 0.0
    # For single-mode, use raw scores
    if mode == "semantic" and sorted_results:
        for r in sorted_results:
            r["score"] = r.get("raw_semantic", r["score"])

    for r in sorted_results:
        r["match_type"] = "+".join(sorted(r["match_type"]))
        del r["rrf_score"]
        r.pop("raw_semantic", None)

    return sorted_results[:top_k]
