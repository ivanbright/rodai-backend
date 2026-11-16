from pathlib import Path

from rodai.benchmark_library import load_catalog


def test_open_road_demo_catalog_preserves_credits_and_review_gates():
    repository_root = Path(__file__).resolve().parents[2]
    catalog = load_catalog(repository_root / "datasets")
    dataset = next(item for item in catalog.datasets if item.id == "open-road-demo")

    assert len(dataset.clips) == 2
    assert all(clip.rights_reviewed for clip in dataset.clips)
    assert all(not clip.privacy_reviewed for clip in dataset.clips)
    assert all(clip.event_type == "unlabeled_road_scene" for clip in dataset.clips)
    assert all(clip.event_time_seconds is None for clip in dataset.clips)
    assert {clip.creator_attribution for clip in dataset.clips} == {
        "01x07x2022000",
        "Lars Mueller",
    }
