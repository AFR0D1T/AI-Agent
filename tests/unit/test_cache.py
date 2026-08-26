from pathlib import Path

from bank_ai_agent.core.cache import FileCache, make_cache_key
from bank_ai_agent.core.llm.client import CachingLLMProvider


def test_make_cache_key_is_stable_and_sensitive_to_inputs() -> None:
    a = make_cache_key(document_text="doc", prompt="p1")
    b = make_cache_key(document_text="doc", prompt="p1")
    c = make_cache_key(document_text="doc", prompt="p2")
    d = make_cache_key(document_text="other doc", prompt="p1")

    assert a == b
    assert a != c
    assert a != d


def test_file_cache_roundtrip(tmp_path: Path) -> None:
    cache = FileCache(tmp_path)
    assert cache.get("missing") is None

    cache.set("key1", {"status": "COMPLIANT"})

    assert cache.get("key1") == {"status": "COMPLIANT"}


def test_caching_provider_calls_inner_only_once_per_key(tmp_path: Path, fake_provider) -> None:
    inner = fake_provider({"status": "COMPLIANT"})
    cache = FileCache(tmp_path)
    caching = CachingLLMProvider(inner, cache)

    r1 = caching.extract(prompt="p", schema={}, document_text="doc")
    r2 = caching.extract(prompt="p", schema={}, document_text="doc")

    assert r1 == r2 == {"status": "COMPLIANT"}
    assert len(inner.calls) == 1  # второй вызов обслужен из кэша
