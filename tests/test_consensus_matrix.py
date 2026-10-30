"""Unit tests for Bridging Consensus Matrix Factorization (Feature 4)."""

from src.graph.consensus_matrix import (
    BridgingConsensusEngine,
    NoteRating,
    NoteStatus,
)

def test_consensus_matrix_bridging_note():
    """A note rated helpful by raters from both opposing ideological sides must be rated helpful."""
    engine = BridgingConsensusEngine(latent_dim=1, max_epochs=80, helpful_threshold=0.30)

    # Raters: user_left_1, user_left_2 (left cluster), user_right_1, user_right_2 (right cluster)
    # note_bridging receives positive ratings (+1.0) from BOTH clusters
    # note_partisan only receives positive ratings from left cluster, negative from right cluster
    ratings = [
        # note_bridging: universally helpful
        NoteRating(rater_id="u_left_1", note_id="note_bridging", rating=1.0),
        NoteRating(rater_id="u_left_2", note_id="note_bridging", rating=1.0),
        NoteRating(rater_id="u_right_1", note_id="note_bridging", rating=1.0),
        NoteRating(rater_id="u_right_2", note_id="note_bridging", rating=1.0),

        # note_partisan: polarized dogpiling
        NoteRating(rater_id="u_left_1", note_id="note_partisan", rating=1.0),
        NoteRating(rater_id="u_left_2", note_id="note_partisan", rating=1.0),
        NoteRating(rater_id="u_right_1", note_id="note_partisan", rating=-1.0),
        NoteRating(rater_id="u_right_2", note_id="note_partisan", rating=-1.0),
    ]

    results = engine.fit_and_score(ratings)
    assert "note_bridging" in results
    assert "note_partisan" in results

    # note_bridging must have higher helpfulness intercept than polarized note
    assert results["note_bridging"].helpfulness_score > results["note_partisan"].helpfulness_score
    assert results["note_bridging"].status == NoteStatus.CURRENTLY_RATED_HELPFUL

def test_consensus_matrix_insufficient_ratings():
    """Notes with fewer than 3 ratings must be marked NEEDS_MORE_RATINGS."""
    engine = BridgingConsensusEngine()
    ratings = [
        NoteRating(rater_id="u1", note_id="note_fresh", rating=1.0),
        NoteRating(rater_id="u2", note_id="note_fresh", rating=1.0),
    ]
    results = engine.fit_and_score(ratings)
    assert results["note_fresh"].status == NoteStatus.NEEDS_MORE_RATINGS

