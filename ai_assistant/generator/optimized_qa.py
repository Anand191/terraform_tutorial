from typing import List, Tuple

import dspy
from dspy.datasets import HotPotQA
from dspy.teleprompt import BootstrapFewShot


def load_dataset(train_size: int = 20, dev_size: int = 50, test_size: int = 0) -> Tuple:
    # Load the dataset.
    dataset = HotPotQA(
        train_seed=1,
        train_size=train_size,
        eval_seed=2023,
        dev_size=dev_size,
        test_size=test_size,
    )
    # Tell DSPy that the 'question' field is the input.
    # Any other fields are labels and/or metadata.
    trainset = [x.with_inputs("question") for x in dataset.train]
    devset = [x.with_inputs("question") for x in dataset.dev]
    return trainset, devset


# Validation logic: check that the predicted answer is correct.
# Also check that the retrieved context does actually contain that answer.
def validate_context_and_answer(example, pred, trace=None):
    answer_EM = dspy.evaluate.answer_exact_match(example, pred)
    answer_PM = dspy.evaluate.answer_passage_match(example, pred)
    return answer_EM and answer_PM


def optimize_generator(module: dspy.Module, trainset: List) -> dspy.Module:
    # Set up a basic teleprompter, which will compile our RAG program.
    teleprompter = BootstrapFewShot(metric=validate_context_and_answer)
    # Compile!
    optimized_module = teleprompter.compile(module, trainset=trainset)
    return optimized_module
