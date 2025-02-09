import requests

def check_grammar(text: str) -> dict:
    """Check grammar using the LanguageTool API."""
    response = requests.post(
        "https://api.languagetool.org/v2/check",
        data={"text": text, "language": "en-US"}
    )
    return response.json()
