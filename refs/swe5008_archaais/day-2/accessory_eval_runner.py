import os, csv, time, re, math
from typing import Dict, Any, List
from dotenv import load_dotenv
from langchain_core.messages import ToolMessage, AIMessage, HumanMessage

from langsmith import Client
from langsmith import evaluate
from langchain_openai import ChatOpenAI
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode, tools_condition
import os
from dotenv import load_dotenv

load_dotenv()
client = Client()
dataset_name = "accessory-golden"

# Load environment variables

openai_key = os.getenv("OPENAI_API_KEY")

class State(TypedDict):
    # Messages have the type "list". The `add_messages` function
    # in the annotation defines how this state key should be updated
    # (in this case, it appends messages to the list, rather than overwriting them)
    messages: Annotated[list, add_messages]

@tool
def get_fashion_accessory_price(code: str) -> float:
    '''Return the price of an accessory given the accessory code
    :param code: accessory code
    :return: price of the accessory
    '''
    return {
        "Orchid Earring": 2.3,
        "Heart Necklace": 1.9,
        "Ruby Ring": 2.5,
        "Bracelet": 3.0
    }.get(code, 0.0)

tools = [get_fashion_accessory_price]

# llm = init_chat_model("google_genai:gemini-2.0-flash")
llm = ChatOpenAI(model="gpt-4o-mini", api_key=openai_key)
llm_with_tools = llm.bind_tools(tools)

def chatbot(state: State):
    return {"messages": [llm_with_tools.invoke(state["messages"] )]}

def build_graph():
    builder = StateGraph(State)
    builder.add_node(chatbot)
    builder.add_node("tools", ToolNode(tools))

    builder.add_edge(START, "chatbot")
    builder.add_conditional_edges("chatbot", tools_condition)
    builder.add_edge("tools", "chatbot")
    graph = builder.compile()
    return graph

graph = build_graph()

# Before running our experiment, we need to upload our dataset to LangSmith.
# 1. We'll read the CSV file and create a dataset with the name "accessory-golden".
import pandas as pd

# Read the dataset CSV file
df = pd.read_csv("accessory_eval_tests1.csv")

# Convert to LangSmith format
examples = []
for _, row in df.iterrows():
    examples.append({
        "inputs": {"prompt": row["prompt"]},
        "outputs": {"expected_total": row["expected_total"]}
    })

# 2. Create dataset in LangSmith
try:
    # Try to read the dataset first to see if it already exists
    existing_dataset = client.read_dataset(dataset_name=dataset_name)
    print(
        f"Dataset '{dataset_name}' already exists with {len(list(client.list_examples(dataset_name=dataset_name)))} examples")
except:
    #Dataset doesn't exist, create it
    dataset = client.create_dataset(
        dataset_name=dataset_name,
        description="accessory dataset for evaluating"
    )

        # Add examples to the dataset
    client.create_examples(
        inputs=[ex["inputs"] for ex in examples],
        outputs=[ex["outputs"] for ex in examples],
        dataset_id=dataset.id
    )

    print(f"Successfully created dataset '{dataset_name}' with {len(examples)} examples")

# 3. define evaluators
def correctness(inputs: dict, outputs: dict, reference_outputs: dict):
    text = outputs["agent_output"]
    pred = extract_last_float(text) if text else None
    expected = reference_outputs["expected_total"]
    exact = False
    if pred is not None:
        exact = abs(pred - expected) <= 1e-3
    return exact

def use_tool(inputs: dict, outputs: dict, reference_outputs: dict):
    #this is demo only.
    #by right, shall implement the comparison of: expected tool call, and the actual output tool call.
    #even can compare the expected no. of tool call, with the actual output no. of tool call
    return outputs["tool_called"]


def extract_first_float(text: str):
    m = re.search(r"[-+]?\d+(?:\.\d+)?", (text or "").replace(",", ""))
    return float(m.group(0)) if m else None

def extract_last_float(text: str):
    s = (text or "").replace(",", "")
    matches = list(re.finditer(r"[-+]?\d+(?:\.\d+)?", s))
    return float(matches[-1].group(0)) if matches else None

# 4. Define a function to run your application
def run(inputs: dict):
    prompt = inputs["prompt"]
    out = graph.invoke({"messages": [HumanMessage(content=prompt)]})
    #{"messages": [{"role": "user", "content": msg}]}
    msgs = out["messages"]
    text = ""
    for m in reversed(msgs):
        if isinstance(m, AIMessage) and m.content:
            text = m.content
            break

    used_tool = any(isinstance(m, ToolMessage) for m in msgs)

    return {
        "agent_output": text,
        "tool_called": bool(used_tool)
    }

# 5. run evaluate
evaluate(
    run,
    data=dataset_name,
    evaluators=[correctness, use_tool],
    experiment_prefix="accessory"
)