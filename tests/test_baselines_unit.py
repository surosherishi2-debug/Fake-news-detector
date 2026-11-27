"""Unit tests for classical baseline utilities and helper functions."""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

from src.evaluation.metrics import compute_classification_metrics
from src.models.baselines import (
    CLASS_NAMES,
    INV_LABEL_MAP,
    LABEL_MAP,
    load_jsonl_samples,
)


def test_label_maps_bijection():
    assert len(LABEL_MAP) == len(INV_LABEL_MAP) == len(CLASS_NAMES) == 3
    for k, v in LABEL_MAP.items():
        assert INV_LABEL_MAP[v] == k


def test_load_jsonl_samples_nonexistent():
    samples = load_jsonl_samples("/nonexistent/file/path/here.jsonl")
    assert isinstance(samples, list)
    assert len(samples) == 0


def test_small_tfidf_lr_pipeline():
    # Synthetic micro dataset covering all 3 classes
    train_texts = [
        "Government reports GDP expansion and job creation confirmed by bureau.",
        "Clinical trials prove new medication is safe and effective.",
        "Conspiracy alleges secret microchips in tap water supply debunked.",
        "Fabricated claim about alien base in Antarctica is false.",
        "Unknown traveler supposedly observed purple cloud on Tuesday.",
        "Uncorroborated rumor concerning unidentified vehicle near park.",
    ]
    train_labels = [0, 0, 1, 1, 2, 2]  # VERIFIED, REFUTED, DATA_VOID

    vec = TfidfVectorizer(ngram_range=(1, 2), max_features=100)
    X_train = vec.fit_transform(train_texts)

    clf = LogisticRegression(C=1.0, random_state=42)
    clf.fit(X_train, train_labels)

    test_texts = [
        "Official bureau confirmed job expansion.",
        "False claim alleges water microchips.",
        "Unconfirmed rumor about unidentified object.",
    ]
    test_labels = [0, 1, 2]

    X_test = vec.transform(test_texts)
    preds = clf.predict(X_test)
    probs = clf.predict_proba(X_test)

    metrics = compute_classification_metrics(test_labels, preds, probs, class_names=CLASS_NAMES)
    assert "accuracy" in metrics
    assert "macro_f1" in metrics
    assert "ece" in metrics
    assert 0.0 <= metrics["accuracy"] <= 1.0
