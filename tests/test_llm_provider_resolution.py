from manus_three_agent.utils.llm import (
    _normalize_provider,
    _redact_secrets,
    _resolve_api_key,
    _resolve_base_url,
)


def test_huggingface_provider_resolution(monkeypatch) -> None:
    monkeypatch.setenv("LLM_PROVIDER", "huggingface")
    monkeypatch.setenv("HF_TOKEN", "hf_abcdefghijklmnopqrstuvwxyz1234567890")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_BASE_URL", raising=False)
    monkeypatch.delenv("HF_BASE_URL", raising=False)

    provider = _normalize_provider("huggingface")
    assert provider == "huggingface"
    assert _resolve_api_key(provider).startswith("hf_")
    assert _resolve_base_url(provider) == "https://router.huggingface.co/v1"


def test_openai_provider_can_fallback_to_hf_token(monkeypatch) -> None:
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("HF_TOKEN", "hf_abcdefghijklmnopqrstuvwxyz1234567890")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_BASE_URL", raising=False)
    monkeypatch.delenv("HF_BASE_URL", raising=False)

    provider = _normalize_provider("openai")
    assert provider == "openai"
    assert _resolve_api_key(provider).startswith("hf_")
    assert _resolve_base_url(provider) == ""


def test_base_url_priority(monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_BASE_URL", "https://custom-openai-compatible.example/v1")
    monkeypatch.setenv("HF_BASE_URL", "https://router.huggingface.co/v1")

    assert _resolve_base_url("huggingface") == "https://custom-openai-compatible.example/v1"


def test_secret_redaction_supports_hf_tokens() -> None:
    text = "token=hf_abcdefghijklmnopqrstuvwxyz1234567890"
    redacted = _redact_secrets(text)
    assert "hf_" not in redacted
    assert "[REDACTED_OPENAI_KEY]" in redacted
