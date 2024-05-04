import dspy

from ai_assistant.retriever.vdb_retrieve import Retrieval


class AdvisorSignature(dspy.Signature):
    # function to call on input to make it a string
    context = dspy.InputField(format=str)
    # function to call on input to make it a string
    question = dspy.InputField()
    answer = dspy.OutputField()


class wiki_assistant(dspy.Module):
    def __init__(self):
        super().__init__()
        self.prog = dspy.ChainOfThought(AdvisorSignature, n=3)

    def forward(self, question, retriver_collection, database_loc):
        retrieved = Retrieval(retriver_collection, database_loc)(question)
        prediction = self.prog(context=retrieved, question=question)
        return dspy.Prediction(context=retrieved, answer=prediction.answer)
