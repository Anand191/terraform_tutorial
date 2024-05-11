import dspy

from ai_assistant.retriever.vdb_retrieve import Retrieval


class AdvisorSignature(dspy.Signature):
    # function to call on input to make it a string
    context = dspy.InputField(format=str)
    question = dspy.InputField()
    answer = dspy.OutputField()


class wiki_assistant(dspy.Module):
    def __init__(self, retriver_collection, database_loc):
        super().__init__()
        self.collection = retriver_collection
        self.db = database_loc
        self.prog = dspy.ChainOfThought(AdvisorSignature, n=3)

    def forward(self, question):
        retrieved = Retrieval(self.collection, self.db)(question)
        prediction = self.prog(context=retrieved, question=question)
        return dspy.Prediction(context=retrieved, answer=prediction.answer)
