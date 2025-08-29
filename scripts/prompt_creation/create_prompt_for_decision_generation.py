import pandas as pd
import os
import random
import sys
sys.path.append(os.getcwd())
from scripts import ADJECTIVES, LANGUAGES, DECISIONS

DIMENSIONS = DECISIONS.keys()

PROMPT = """I want to construct decision problems that involve two lists of concepts. CONCEPT 1: <LIST1>. CONCEPT 2: <LIST2>. One example is: 
'<TASK>'

Generate another decision problem replicating the general structure of the example above but in different domains. I want to probe for the dimension "<DIMENSION>". Do not change the two lists of concepts. Give me 10 decision scenarios:"""

for dimension in DIMENSIONS:
    if "-1" in dimension:
        concept1 = DECISIONS[dimension][0]
        concept2 = DECISIONS[dimension][1]
        task_prompt = DECISIONS[dimension][2]

        prompt = PROMPT.replace("<LIST1>", str(concept1))
        prompt = prompt.replace("<LIST2>", str(concept2))

        prompt = prompt.replace("<DIMENSION>", dimension.replace("-1", ""))
        prompt = prompt.replace("<TASK>", task_prompt[0])

        prompt = prompt.replace("Writer A", "Person A")
        prompt = prompt.replace("Writer B", "Person B")

        print("\n\n------Prompt to generate dimension {}:------".format(dimension))
        print(prompt)
