from pathlib import Path

PROMPTS_DIR = Path(__file__).parent


def load_prompt(name: str, variables: dict | None = None) -> str:
    prompt_file = PROMPTS_DIR / f"{name}.md"
    if not prompt_file.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_file}")

    content = prompt_file.read_text(encoding="utf-8").strip()

    if variables:
        for key, value in variables.items():
            content = content.replace(f"{{{key}}}", str(value))

    return content
