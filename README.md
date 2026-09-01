# SkillFlow

![Flo, the SkillFlow mascot, surfing a rainbow pipeline of reusable skills](docs/flo.jpg)

Meet **Flo** — SkillFlow's mascot, riding a pipeline of small, reusable skills.

SkillFlow is a minimal "Kubeflow for agents" framework. Skills stay small and stable. Task-specific prompts live outside the skill. Recipes compose skills into linear workflows.

## Philosophy

- **Skills are stable.** A skill is a small, reusable component with a Pydantic Input and Output. When models improve, the skill almost never needs to change.
- **Specificity can churn.** Prompts, tone, and task details live in `specificity/` as Markdown or YAML. Edit those files freely.
- **Recipes compose.** A recipe is a linear pipeline. The runner adapts one skill's Output into the next skill's Input and logs the JSON in between.
- **Deterministic and LLM skills mix.** Search can be plain Python. Extract and Summarize can call a model through a thin `LLMClient`.

## Run the research example

```bash
uv sync --group dev
uv run python recipes/research.py "What is Kubeflow?"
```

The recipe is Search → Extract → Summarize. Intermediate Pydantic models are logged as JSON.

### Local Ollama (Apple Silicon)

This machine-friendly default keeps examples free to run:

```bash
brew install ollama
brew services start ollama
ollama pull qwen3:8b
curl http://localhost:11434/v1/models
```

| Role | Model | Notes |
| --- | --- | --- |
| Default | `qwen3:8b` (~5.2 GB) | Fast enough for iteration on a 32 GB M5 Mac |
| Optional upgrade | `qwen3:14b` (~9.3 GB) | Still comfortable if you want more quality |

Copy [`.env.example`](.env.example) if you want to override the defaults. The client disables Qwen3 "thinking" tokens so Extract and Summarize return clean text.

### Swap to a hosted model later

Keep the skills. Change environment variables:

```bash
export SKILLFLOW_LLM_BASE_URL=https://api.openai.com/v1
export SKILLFLOW_LLM_API_KEY=sk-...
export SKILLFLOW_LLM_MODEL=gpt-4.1-mini
```

## Development

Requires [uv](https://docs.astral.sh/uv/) and Python 3.12+.

```bash
make sync
make hooks
make lint
make test
```

Equivalent `uv` commands:

```bash
uv sync --group dev
uv run pre-commit install
uv run ruff check .
uv run ruff format .
uv run pytest
```
