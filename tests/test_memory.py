from memoir_agent.memory import MemoryStore


def test_save_and_search_ranks_tags_and_title_over_body(tmp_path):
    s = MemoryStore(tmp_path)
    s.save("Summer at the lake", "We fished every morning.", ["childhood"])
    s.save("First job", "Worked at the lake marina for a summer.", ["work"])
    hits = s.search("lake summer")
    assert [m.title for m in hits] == ["Summer at the lake", "First job"]


def test_duplicate_titles_do_not_overwrite(tmp_path):
    s = MemoryStore(tmp_path)
    s.save("Dad", "one")
    s.save("Dad", "two")
    assert {m.body for m in s.all()} == {"one", "two"}


def test_search_no_match_returns_empty(tmp_path):
    s = MemoryStore(tmp_path)
    s.save("Dad", "fishing")
    assert s.search("submarine") == []


def test_roundtrip_tags(tmp_path):
    s = MemoryStore(tmp_path)
    s.save("Mom", "baking", ["Family", " home "])
    assert s.all()[0].tags == ("family", "home")
