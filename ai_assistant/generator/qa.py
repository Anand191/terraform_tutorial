import re

import dspy


def assertions_context(answer: str) -> bool:
    regex = re.compile(r"^Context:|^.*.*Context")
    return bool(re.match(regex, answer))


def assertions_empty(answer: str) -> bool:
    cond1 = answer == "N/A"
    cond2 = answer == ""
    return cond1 or cond2


class AdvisorSignature(dspy.Signature):
    """
    Answer the question within 200 words based on the given context.
    """

    context = dspy.InputField(desc="may contain relevant facts")
    question = dspy.InputField()
    answer = dspy.OutputField(
        desc="concise, coherent and complete answer, based on context"
    )


class wiki_assistant(dspy.Module):
    def __init__(self, num_passages=3):
        super().__init__()
        self.retrieve = dspy.Retrieve(k=num_passages)
        self.prog = dspy.ChainOfThought(AdvisorSignature)

    def forward(self, question):
        retrieved = self.retrieve(question).passages
        prediction = self.prog(context=retrieved, question=question)
        dspy.Suggest(
            assertions_context(prediction.answer),
            "If answer begins with 'Context:' regenerate answer",
        )
        dspy.Suggest(
            assertions_empty(prediction.answer),
            "If context is available then answer must not be empty or N/A",
        )
        return dspy.Prediction(context=retrieved, answer=prediction.answer)
