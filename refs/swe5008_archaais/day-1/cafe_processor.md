### Prompt

SYSTEM_PROMPT = """
You are a high-accuracy order processing engine for a cafe. Your task is to extract food and drink orders from natural language and convert them into a strict JSON format.

Rules:

1. Item Name: Standardize the item name.
2. Quantity: Extract numerical values. Default to 1 for "a/an".
3. Size: Default to "regular" unless specified.
4. Total: Sum all quantities in "total_items".
5. Output: Return ONLY valid JSON.
   """

### Results

Input: 2x Americano, 1 large fries and 3 hamburger
Output: {
"orders": [
{
"item_name": "Americano",
"quantity": 2,
"size": "regular"
},
{
"item_name": "fries",
"quantity": 1,
"size": "large"
},
{
"item_name": "hamburger",
"quantity": 3,
"size": "regular"
}
],
"total_items": 6
}

---

Input: I'll have a cappuccino and two croissants please
Output: {
"orders": [
{
"item_name": "cappuccino",
"quantity": 1,
"size": "regular"
},
{
"item_name": "croissant",
"quantity": 2,
"size": "regular"
}
],
"total_items": 3
}

---

Input: Can I get three iced lattes, make one of them decaf
Output: {
"orders": [
{
"item_name": "iced latte",
"quantity": 2,
"size": "regular"
},
{
"item_name": "iced latte",
"quantity": 1,
"size": "regular",
"special_request": "decaf"
}
],
"total_items": 3
}

---

Input: One burger meal with coke, and an extra order of fries
Output: {
"orders": [
{
"item_name": "burger meal",
"quantity": 1,
"size": "regular"
},
{
"item_name": "coke",
"quantity": 1,
"size": "regular"
},
{
"item_name": "fries",
"quantity": 1,
"size": "regular"
}
],
"total_items": 3
}

---

Input: Give me a small mocha and two large lattes
Output: {
"orders": [
{
"item_name": "mocha",
"quantity": 1,
"size": "small"
},
{
"item_name": "latte",
"quantity": 2,
"size": "large"
}
],
"total_items": 3
}

---
