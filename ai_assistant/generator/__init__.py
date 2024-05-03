import os

import dotenv
import dspy
from dsp.modules import GoogleVertexAI


def init_gemini_pro(temperature: float = 0.0):
    """
    Initializes dspy to use Gemini as the language model.
    """
    dotenv.load_dotenv("api_keys.env")
    api_key = os.getenv("GOOGLE_API_KEY")
    gemini = GoogleVertexAI(
        model_name="gemini-1.0-pro", project="deft-weaver-396616", location="us-central1", credentials=api_key
    )
    # gemini = dspy.Google(
    #     "models/gemini-1.0-pro",
    #     api_key=api_key,
    #     temperature=temperature
    # )
    dspy.settings.configure(lm=gemini, max_tokens=1024)
