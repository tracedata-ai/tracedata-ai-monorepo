import json
import os
from openai import OpenAI
from dotenv import load_dotenv

def get_fleet_support_response(fleet_data):
    """
    Sends fleet data to an AI assistant configured as the Fleet Support Agent.
    """
    # Load .env from the parent directory
    dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    load_dotenv(dotenv_path=dotenv_path)
    
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    # System prompt based on docs\agents\4_support_agent.md
    system_prompt = (
        "You are the Fleet Management Support Agent. Your role is to analyze telematics data "
        "and driver reports to provide constructive feedback, safety tips, and educational guidance "
        "to fleet drivers. Your tone should be professional, supportive, and safety-oriented. "
        "Focus on helping the driver improve and grow. Always refer to specific data points provided."
    )

    user_message = (
        f"A driver incident has been reported. Please analyze the following fleet data and "
        f"provide improvement tips and learning recommendations:\n\n"
        f"```json\n{json.dumps(fleet_data, indent=2)}\n```"
    )

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        temperature=0.7
    )

    return response.choices[0].message.content

if __name__ == "__main__":
    # Example fleet data provided by user
    example_fleet_data = {
        "event_id": "EVT-99821",
        "driver_id": "DRV-4412",
        "trip_metadata": {
            "timestamp": "2026-03-16T14:30:05Z",
            "location": {
                "lat": 1.29027,
                "long": 103.851959
            },
            "telemetry_incident": "Hard Braking (9.2 m/s²)"
        },
        "driver_input": {
            "text": "harsh break",
            "category": "safety_incident_appeal"
        }
    }

    print("--- Sending Fleet Data to Support Agent ---\n")
    support_feedback = get_fleet_support_response(example_fleet_data)
    print("--- Support Agent Feedback ---\n")
    print(support_feedback)
