import os

import dspy
from dsp.modules import GoogleVertexAI
from google.oauth2 import service_account

from ai_assistant.utils.global_utils import load_conf, load_env

load_env()
project_root = os.environ.get("ROOT")
google_api_key = os.environ.get("GOOGLE_API_KEY")
cfg = load_conf(project_root)


def init_gemini_pro(temperature: float = 0.0):
    """
    Initializes dspy to use Gemini as the language model.
    """
    credentials = service_account.Credentials.from_service_account_file(google_api_key)
    gemini = GoogleVertexAI(
        model_name=cfg["llm"]["model"], project=cfg["project"], location=cfg["llm"]["location"], credentials=credentials
    )
    dspy.settings.configure(lm=gemini, temperature=temperature, max_tokens=1024)
