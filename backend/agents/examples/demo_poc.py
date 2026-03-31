"""Demo: Phase 1 PoC - WeatherTrafficAgent with OpenAI."""

import sys
from backend.common.llm import load_llm, OpenAIModel
from backend.agents.examples import WeatherTrafficAgent


def main():
    """Run PoC demo."""
    print("=" * 70)
    print("PHASE 1 PoC DEMO: Weather/Traffic Agent with LLM")
    print("=" * 70)
    print()

    # Step 1: Load LLM via factory
    print("Step 1: Loading OpenAI LLM via factory pattern...")
    try:
        config = load_llm(OpenAIModel.GPT_4O)
        print(f"  ✓ Provider: {config.provider}")
        print(f"  ✓ Model: {config.model}")
        print()
    except EnvironmentError as e:
        print(f"  ✗ Error: {e}")
        print()
        print("  Set OPENAI_API_KEY environment variable to run this demo")
        return 1

    # Step 2: Get chat model from adapter
    print("Step 2: Getting chat model from adapter...")
    llm = config.adapter.get_chat_model()
    print(f"  ✓ LLM initialized: {type(llm).__name__}")
    print()

    # Step 3: Create WeatherTrafficAgent
    print("Step 3: Creating WeatherTrafficAgent with tools...")
    agent = WeatherTrafficAgent(llm=llm)
    print(f"  ✓ Agent: {agent.agent_name}")
    print(f"  ✓ Tools: {[t.name for t in agent.tools]}")
    print(f"  ✓ System Prompt (first 100 chars): {agent.system_prompt[:100]}...")
    print()

    # Step 4: Invoke agent with sample query
    print("Step 4: Invoking agent with sample query...")
    query = {
        "messages": [
            {
                "role": "user",
                "content": "I need to drive in Singapore today. Is it safe? Check weather and traffic.",
            }
        ]
    }

    try:
        result = agent.invoke(query)
        print("  ✓ Agent invocation complete!")
        print()
        print("  Result keys:", list(result.keys()))
        if "messages" in result:
            print(f"  Number of messages in result: {len(result['messages'])}")
            # Print the final response message
            for msg in result["messages"][-3:]:
                print(f"\n  Message ({getattr(msg, 'type', 'unknown')}):")
                content = getattr(msg, "content", str(msg))
                # Truncate for display
                if isinstance(content, str) and len(content) > 300:
                    print(f"    {content[:300]}...")
                else:
                    print(f"    {content}")
    except Exception as e:
        print(f"  ✗ Error during invocation: {e}")
        import traceback

        traceback.print_exc()
        return 1

    print()
    print("=" * 70)
    print("✓ PHASE 1 PoC SUCCESSFUL!")
    print("=" * 70)
    print()
    print("Summary:")
    print("  - LLM adapter factory pattern works")
    print("  - Agent ABC with LangGraph integration works")
    print("  - Tools (@tool decorator) integrate with agent")
    print("  - System prompts guide agent behavior")
    print()
    print("Next: Phase 2 will add domain-specific tools (scoring, safety, etc.)")
    print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
