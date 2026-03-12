import json
from openai import OpenAI

client = OpenAI()

SYSTEM_PROMPT = """
You are a high-accuracy order processing engine for a cafe. Your task is to extract food and drink orders from natural language and convert them into a strict JSON format.

Rules:
1. Item Name: Standardize the item name.
2. Quantity: Extract numerical values. Default to 1 for "a/an".
3. Size: Default to "regular" unless specified.
4. Total: Sum all quantities in "total_items".
5. Output: Return ONLY valid JSON.
"""


def process_order(customer_input):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": customer_input},
            ],
            temperature=0.1,
            response_format={"type": "json_object"},
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        return {"error": str(e)}


# Test Suite
orders = [
    "2x Americano, 1 large fries and 3 hamburger",
    "I'll have a cappuccino and two croissants please",
    "Can I get three iced lattes, make one of them decaf",
    "One burger meal with coke, and an extra order of fries",
    "Give me a small mocha and two large lattes",
]

if __name__ == "__main__":
    for order in orders:
        print(f"Input: {order}")
        structured_data = process_order(order)
        print(f"Output: {json.dumps(structured_data, indent=2)}")
        print("-" * 30)
