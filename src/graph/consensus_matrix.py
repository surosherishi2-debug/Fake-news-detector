"""Decentralized Bridging Consensus Engine using Matrix Factorization.

Implements the open-source X/Twitter Community Notes consensus scoring algorithm:
Identifies whether a community fact-checking note achieves consensus across
ideologically polarized user clusters in a low-dimensional latent space.

Mathematical Formulation:
    r_hat_{ui} = μ + b_u + b_i + p_u^T * q_i
Where:
    - μ is the global rating intercept
    - b_u is the rater baseline bias
    - b_i is the note core helpfulness intercept (The Bridging Metric)
    - p_u is the rater latent factor vector (ideological polarity)
    - q_i is the note latent factor vector
"""

from typing import Dict, List, Tuple, Optional
from enum import Enum
import numpy as np
from pydantic import BaseModel, Field

class NoteStatus(str, Enum):
    CURRENTLY_RATED_HELPFUL = "CURRENTLY_RATED_HELPFUL"
    CURRENTLY_RATED_NOT_HELPFUL = "CURRENTLY_RATED_NOT_HELPFUL"
    NEEDS_MORE_RATINGS = "NEEDS_MORE_RATINGS"

class NoteRating(BaseModel):
    rater_id: str
    note_id: str
    rating: float = Field(..., ge=-1.0, le=1.0, description="1.0 = Helpful, 0.0 = Somewhat, -1.0 = Not Helpful")

class NoteScoringResult(BaseModel):
    note_id: str
    status: NoteStatus
    helpfulness_score: float = Field(..., description="Bridging intercept b_i")
    rater_agreement_variance: float
    total_ratings: int
    latent_polarization_factor: float

class BridgingConsensusEngine:
    """
    Classical Machine Learning Matrix Factorization for Bipartisan Consensus.
    Mathematically rewards notes supported by ideologically diverse raters.
    """

    def __init__(
        self,
        latent_dim: int = 1,
        learning_rate: float = 0.05,
        reg_bias: float = 0.03,
        reg_factor: float = 0.05,
        max_epochs: int = 100,
        helpful_threshold: float = 0.35,
        not_helpful_threshold: float = -0.20,
    ):
        self.latent_dim = latent_dim
        self.lr = learning_rate
        self.reg_bias = reg_bias
        self.reg_factor = reg_factor
        self.max_epochs = max_epochs
        self.helpful_threshold = helpful_threshold
        self.not_helpful_threshold = not_helpful_threshold

    def fit_and_score(self, ratings: List[NoteRating]) -> Dict[str, NoteScoringResult]:
        """
        Fit matrix factorization model on rater-note ratings matrix and compute bridging scores.
        
        Args:
            ratings: List of NoteRating objects.
            
        Returns:
            Dict[note_id, NoteScoringResult]: Calibrated note statuses and scores.
        """
        if not ratings:
            return {}

        # 1. Map IDs to matrix indices
        unique_raters = list({r.rater_id for r in ratings})
        unique_notes = list({r.note_id for r in ratings})
        
        rater_map = {r_id: idx for idx, r_id in enumerate(unique_raters)}
        note_map = {n_id: idx for idx, n_id in enumerate(unique_notes)}

        n_raters = len(unique_raters)
        n_notes = len(unique_notes)

        # 2. Extract rating triples (u, i, r)
        triples: List[Tuple[int, int, float]] = [
            (rater_map[r.rater_id], note_map[r.note_id], r.rating)
            for r in ratings
        ]

        # Global mean rating
        global_mu = float(np.mean([t[2] for t in triples]))

        # 3. Initialize parameters
        b_u = np.zeros(n_raters, dtype=np.float64)
        b_i = np.zeros(n_notes, dtype=np.float64)
        P = np.random.normal(0.0, 0.1, size=(n_raters, self.latent_dim))
        Q = np.random.normal(0.0, 0.1, size=(n_notes, self.latent_dim))

        # 4. Stochastic Gradient Descent with L2 Regularization
        for epoch in range(self.max_epochs):
            np.random.shuffle(triples)
            for u, i, r in triples:
                # Prediction
                pred = global_mu + b_u[u] + b_i[i] + float(np.dot(P[u], Q[i]))
                err = r - pred

                # Update biases
                b_u[u] += self.lr * (err - self.reg_bias * b_u[u])
                b_i[i] += self.lr * (err - self.reg_bias * b_i[i])

                # Update latent factors
                p_old = P[u].copy()
                P[u] += self.lr * (err * Q[i] - self.reg_factor * P[u])
                Q[i] += self.lr * (err * p_old - self.reg_factor * Q[i])

        # 5. Compile Results per Note
        results: Dict[str, NoteScoringResult] = {}
        note_ratings_count: Dict[str, List[float]] = {n: [] for n in unique_notes}
        for r in ratings:
            note_ratings_count[r.note_id].append(r.rating)

        for n_id, i in note_map.items():
            r_list = note_ratings_count[n_id]
            b_val = float(b_i[i])
            q_factor = float(np.linalg.norm(Q[i]))
            variance = float(np.var(r_list)) if len(r_list) > 1 else 0.0

            # Determine Community Notes Status
            # A note must have minimum number of ratings (e.g. >= 3) to achieve helpful status
            if len(r_list) < 3:
                status = NoteStatus.NEEDS_MORE_RATINGS
            elif b_val >= self.helpful_threshold:
                status = NoteStatus.CURRENTLY_RATED_HELPFUL
            elif b_val <= self.not_helpful_threshold:
                status = NoteStatus.CURRENTLY_RATED_NOT_HELPFUL
            else:
                status = NoteStatus.NEEDS_MORE_RATINGS

            results[n_id] = NoteScoringResult(
                note_id=n_id,
                status=status,
                helpfulness_score=round(b_val, 3),
                rater_agreement_variance=round(variance, 3),
                total_ratings=len(r_list),
                latent_polarization_factor=round(q_factor, 3),
            )

        return results

