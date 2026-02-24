#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RAW_DIR="$ROOT_DIR/references/raw"
META_CSV="$ROOT_DIR/references/REFERENCE_SOURCES.csv"

mkdir -p "$RAW_DIR"

cat > "$META_CSV" <<'CSV'
file,url,downloaded_at_utc,http_status
CSV

while IFS='|' read -r filename url; do
  [ -z "$filename" ] && continue
  out="$RAW_DIR/$filename"

  # Keep downloading resilient but deterministic.
  code=$(curl -L --retry 2 --connect-timeout 10 --max-time 60 \
    -A "Mozilla/5.0 (Codex Reference Downloader)" \
    -w "%{http_code}" -o "$out" -s "$url" || true)

  ts=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
  printf '%s,%s,%s,%s\n' "$filename" "$url" "$ts" "$code" >> "$META_CSV"

  if [ "$code" -ge 400 ] || [ "$code" -lt 200 ]; then
    echo "[WARN] $url -> HTTP $code"
  else
    echo "[OK]   $url -> $out"
  fi
done <<'URLS'
manus_home.html|https://manus.im/
manus_blog.html|https://manus.im/blog
manus_feature_browser_operator.html|https://manus.im/features/manus-browser-operator
manus_feature_wide_research.html|https://manus.im/features/wide-research
manus_feature_webapp.html|https://manus.im/features/webapp
manus_docs.html|https://manus.im/docs
manus_open_docs.html|https://open.manus.ai/docs
openai_python_github.html|https://github.com/openai/openai-python
openai_agents_github.html|https://github.com/openai/openai-agents-python
openai_agents_docs_home.html|https://openai.github.io/openai-agents-python/
openai_agents_docs_tracing.html|https://openai.github.io/openai-agents-python/tracing/
langgraph_github.html|https://github.com/langchain-ai/langgraph
langgraph_docs.html|https://langchain-ai.github.io/langgraph/
otel_python_docs.html|https://opentelemetry.io/docs/languages/python/
otel_tracing_concepts.html|https://opentelemetry.io/docs/concepts/signals/traces/
phoenix_github.html|https://github.com/Arize-ai/phoenix
URLS

