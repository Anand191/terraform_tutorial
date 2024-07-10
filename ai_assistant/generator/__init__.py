import os

from dsp.modules import GoogleVertexAI
from dspy import AzureOpenAI
from google.oauth2 import service_account

from ai_assistant.utils.global_utils import load_conf, load_env

load_env()
project_root = os.environ.get("ROOT")
google_api_key = os.environ.get("GOOGLE_API_KEY")
azure_api = os.environ.get("AZURE_OPENAI_ENDPOINT")
azure_key = os.environ.get("AZURE_OPENAI_API_KEY")
cfg = load_conf(project_root)


def init_gemini_pro(temperature: float = 0.0):
    """
    Initializes dspy to use Gemini as the language model.
    """
    credentials = service_account.Credentials.from_service_account_file(google_api_key)
    gemini = GoogleVertexAI(
        model_name=cfg["gcp"]["llm"]["model"],
        project=cfg["gcp"]["project"],
        location=cfg["gcp"]["llm"]["location"],
        credentials=credentials,
    )
    return gemini


def init_openai(temperature: float = 0.0):
    """
    Initializes dspy to use GPT as the language model
    """
    gpt = AzureOpenAI(
        api_base=azure_api,
        api_key=azure_key,
        model=cfg["azure"]["llm"]["model"],
        api_version=cfg["azure"]["llm"]["version"],
        model_type="chat",
        temperature=temperature,
    )
    return gpt
