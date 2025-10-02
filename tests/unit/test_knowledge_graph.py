"""Unit tests for the knowledge graph utility."""

import math
import pytest
from synthetic_data_kit.utils.knowledge_graph import generate_knowledge_graph


def _find_node(graph, node_id):
    return next((node for node in graph["nodes"] if node["id"] == node_id), None)


def _edge_exists(graph, expected):
    for edge in graph["edges"]:
        if {edge["source"], edge["target"]} == set(expected):
            return edge
    return None


def test_generate_knowledge_graph_basic_structure():
    qa_pairs = [
        {
            "question": "What is the capital of France?",
            "answer": "Paris is the capital and the most populous city of France.",
        },
        {
            "question": "Which city is known as the City of Light?",
            "answer": "Paris is often called the City of Light because of its leading role in the Age of Enlightenment.",
        },
        {
            "question": "Which river runs through Paris?",
            "answer": "The Seine river flows through the heart of Paris in France.",
        },
    ]

    graph = generate_knowledge_graph(qa_pairs, max_nodes=10, max_edges=10, min_cooccurrence=1)

    assert graph["metadata"]["input_pairs"] == 3
    node_ids = {node["id"] for node in graph["nodes"]}
    assert "paris" in node_ids
    assert "france" in node_ids

    paris_node = _find_node(graph, "paris")
    assert paris_node is not None
    assert paris_node["occurrences"] >= 3
    assert paris_node["weight"] >= 3
    assert paris_node["degree"] > 0

    france_edge = _edge_exists(graph, {"paris", "france"})
    assert france_edge is not None
    assert france_edge["weight"] >= 2


def test_generate_knowledge_graph_respects_weighting_and_filters():
    qa_pairs = [
        {"question": "Alpha?", "answer": "Alpha connects with beta.", "rating": 0.5},
        {"question": "Gamma?", "answer": "Alpha relates closely to gamma.", "rating": 3},
    ]

    graph = generate_knowledge_graph(
        qa_pairs,
        max_nodes=5,
        max_edges=5,
        min_cooccurrence=1.0,
        additional_stopwords=["relates"],
    )

    alpha = _find_node(graph, "alpha")
    beta = _find_node(graph, "beta")
    gamma = _find_node(graph, "gamma")

    assert alpha is not None
    assert beta is not None
    assert gamma is not None

    assert alpha["weight"] == pytest.approx(3.5)
    assert beta["weight"] < alpha["weight"]
    assert gamma["weight"] < alpha["weight"]

    edge_alpha_gamma = _edge_exists(graph, {"alpha", "gamma"})
    assert edge_alpha_gamma is not None
    assert edge_alpha_gamma["weight"] == pytest.approx(3.0)

    # Edge with weight below min_cooccurrence should be dropped
    assert _edge_exists(graph, {"alpha", "beta"}) is None