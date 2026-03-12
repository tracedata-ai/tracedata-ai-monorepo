import os
import asyncio
from typing import Optional, List, Union

from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.output_parsers import PydanticOutputParser

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")

# ----------------------------
# Config
# ----------------------------
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.4"))

topic = (
    #"Should basic financial literacy be a required part of secondary school curricula?"
    "The two circles are externally tangent and there is no relative sliding. "
    "The radius of circle A is 1/3 the radius of circle B. Circle A rolls "
    "around circle B one trip back to its starting point. How many times will "
    "circle A revolve in total?"
)

# ----------------------------
# Agents
# ----------------------------
class DebateAgent:
    def __init__(self, name: str, side_brief: str):
        self.name = name
        self.llm = ChatOpenAI(model=OPENAI_MODEL, temperature=TEMPERATURE, api_key=API_KEY)

        # Prompt includes round context to discourage early finalization
        self.prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessage(
                    content=(
                        f"You are a debater named {name}. {side_brief} "
                        "Debate professionally. Use concrete reasons and short examples. "
                        "Avoid hallucinations. Be concise (6–10 sentences). "
                        "Do NOT declare final consensus or final recommendation "
                        "until at least {min_rounds} rounds have been completed."
                    )
                ),
                SystemMessage(content=f"Debate topic:\n{topic}"),
                MessagesPlaceholder("transcript"),
                HumanMessage(
                    content=(
                        "Round {round_idx}. Provide your next response. "
                        "If you must propose a tentative position, mark it as TENTATIVE. "
                        "If we are past the minimum rounds and positions converge, you may support CONSENSUS."
                    )
                ),
            ]
        )

    async def respond(self, transcript: List[Union[AIMessage, HumanMessage]], round_idx: int, min_rounds: int):
        chain = self.prompt | self.llm
        result = await chain.ainvoke(
            {"transcript": transcript, "round_idx": round_idx, "min_rounds": min_rounds}
        )
        return AIMessage(content=result.content, name=self.name)


class JudgeModel(BaseModel):
    finished: bool = Field(description="Whether to end the debate now.")
    consensus: bool = Field(description="True if the two sides have converged on a practical recommendation.")
    proposed_answer: Optional[str] = Field(
        default=None,
        description="If consensus is True, state the agreed recommendation in one sentence; else null.",
    )
    rationale: str = Field(
        description="Brief justification (2–4 sentences) explaining the decision and next step if not finished."
    )


class ModeratorAgent:
    def __init__(self, min_rounds: int, max_rounds: int):
        self.llm = ChatOpenAI(model=OPENAI_MODEL, temperature=0.0, api_key=API_KEY)
        self.parser = PydanticOutputParser(pydantic_object=JudgeModel)
        self.min_rounds = min_rounds

        self.prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessage(
                    content=(
                        "You are a fair, practical moderator. Review the latest two arguments. "
                        "Your job is to strongly guide toward consensus but NOT finish early. "
                        f"Do NOT set finished=true until at least {min_rounds} rounds have completed "
                        "AND you detect clear consensus (positions substantially align). "
                        "When not finished, suggest the next sub-issue to debate."
                        f"When {max_rounds} rounds have completed, consensus can be True if the two sides have converged on a practical recommendation."
                    )
                ),
                SystemMessage(content=f"Debate topic:\n{topic}"),
                MessagesPlaceholder("latest_round"),
                HumanMessage(
                    content=(
                        "Return STRICT JSON with keys: finished (bool), consensus (bool), "
                        "proposed_answer (string or null), rationale (string). "
                        "\n\nOutput schema:\n{schema_placeholder}"
                    )
                ),
            ]
        )

    async def judge(self, latest_round: List[AIMessage]):
        chain = self.prompt.partial(
            schema_placeholder=self.parser.get_format_instructions()
        ) | self.llm | self.parser
        return await chain.ainvoke({"latest_round": latest_round})


# ----------------------------
# Orchestrator
# ----------------------------
async def run_multiagent_debate(max_rounds: int = 4, min_rounds: int = 0):
    alice = DebateAgent(
        name="Alice",
        side_brief="You are affirmative side, Please express your viewpoints."
    )
    bob = DebateAgent(
        name="Bob",
        side_brief="You are negative side. Provide your reason and answer."
    )
    moderator = ModeratorAgent(min_rounds=min_rounds, max_rounds=max_rounds)

    transcript: List[Union[AIMessage, HumanMessage]] = []

    for round_idx in range(1, max_rounds + 1):
        print(f"\n=== Round {round_idx} ===")

        alice_msg = await alice.respond(transcript, round_idx, min_rounds)
        transcript.append(alice_msg)
        print(f"\nAlice:\n{alice_msg.content}")

        bob_msg = await bob.respond(transcript, round_idx, min_rounds)
        transcript.append(bob_msg)
        print(f"\nBob:\n{bob_msg.content}")

        judge = await moderator.judge([alice_msg, bob_msg])
        # Enforce our gate: never finish before min_rounds
        should_finish = judge.finished and judge.consensus and (round_idx >= min_rounds)

        print(
            f"\n[Moderator] finished={judge.finished}, consensus={judge.consensus}\n"
            f"rationale: {judge.rationale}\n"
            f"proposed_answer: {judge.proposed_answer}"
        )

        if should_finish:
            print("\n✅ Debate finished with consensus:")
            print(judge.proposed_answer or "(no answer provided)")
            return

    print("\n⏱️ Max rounds reached. No enforced consensus; consider increasing max_rounds or relaxing min_rounds.")


if __name__ == "__main__":
    asyncio.run(run_multiagent_debate(max_rounds=5, min_rounds=0))
