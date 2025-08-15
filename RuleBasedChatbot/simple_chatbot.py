# simple_chatbot.py
import re
import random
import sys

# Simple response templates
RESPONSES = {
    "greeting": ["Hi! How can I help you today?", "Hello! What can I do for you?", "Hey there!"],
    "bye": ["Goodbye! Have a nice day.", "See you later!", "Bye!"],
    "thanks": ["You're welcome!", "No problem!", "Happy to help!"],
    "name_reply": ["Nice to meet you, {name}!", "Got it — I'll call you {name}."],
    "ask_name": ["What's your name?", "May I know your name?"],
    "help": ["I can greet you, remember your name, do simple math (e.g. 2 + 3), and respond to a few common intents."],
    "unknown": ["Sorry, I didn't understand that. Could you rephrase?", "I don't know how to respond to that yet."],
    "age": ["I am a simple rule-based chatbot (no real age!)."],
}

# Patterns that map user text to intents
PATTERNS = {
    "greeting": [r"\bhi\b", r"\bhello\b", r"\bhey\b", r"\bgood (morning|afternoon|evening)\b"],
    "bye": [r"\bbye\b", r"\bgoodbye\b", r"\bsee you\b", r"\bexit\b", r"\bquit\b"],
    "thanks": [r"\bthank\b", r"\bthanks\b", r"\bthx\b"],
    "ask_name": [r"\bwhat(?:'s| is) your name\b", r"\bwho are you\b", r"\bwhat are you\b"],
    "provide_name": [r"\bmy name is (\w+)\b", r"\bi am (\w+)\b", r"\bi'm (\w+)\b", r"\bcall me (\w+)\b"],
    "help": [r"\bhelp\b", r"\bwhat can you do\b", r"\bcommands?\b"],
    "age": [r"\bage\b", r"\bhow old are you\b"],
    # math handled separately with regex
}

EXIT_KEYWORDS = {"exit", "quit", "bye", "goodbye", "see you"}

def preprocess(text: str) -> str:
    """Lowercase and remove punctuation (simple)."""
    text = text.lower().strip()
    # remove punctuation except + - * / . (for math)
    text = re.sub(r"[^\w\s\+\-\*\/\.]", "", text)
    return text

def find_intents(text: str):
    """
    Returns a list of detected intents (may be multiple).
    Also returns captured groups (e.g., a provided name).
    """
    intents = []
    captures = {}
    for intent, patterns in PATTERNS.items():
        for pat in patterns:
            m = re.search(pat, text)
            if m:
                intents.append(intent)
                # if a name was captured, save it
                if intent == "provide_name" and m.groups():
                    captures["name"] = m.group(1).capitalize()
                break
    # check for simple math expressions: number op number
    math_m = re.search(r"(-?\d+(?:\.\d+)?)\s*([\+\-\*\/])\s*(-?\d+(?:\.\d+)?)", text)
    if math_m:
        intents.append("math")
        captures["math"] = (math_m.group(1), math_m.group(2), math_m.group(3))
    return intents, captures

def handle_intents(intents, captures, state):
    """Return a response (string)."""
    if not intents:
        return random.choice(RESPONSES["unknown"])

    out_responses = []
    for intent in intents:
        if intent == "greeting":
            out_responses.append(random.choice(RESPONSES["greeting"]))
        elif intent == "bye":
            out_responses.append(random.choice(RESPONSES["bye"]))
            state["should_exit"] = True
        elif intent == "thanks":
            out_responses.append(random.choice(RESPONSES["thanks"]))
        elif intent == "ask_name":
            if state.get("user_name"):
                out_responses.append(f"You're {state['user_name']}, right?")
            else:
                out_responses.append(random.choice(RESPONSES["ask_name"]))
        elif intent == "provide_name":
            name = captures.get("name")
            if name:
                state["user_name"] = name
                out_responses.append(random.choice(RESPONSES["name_reply"]).format(name=name))
        elif intent == "help":
            out_responses.append(random.choice(RESPONSES["help"]))
        elif intent == "age":
            out_responses.append(random.choice(RESPONSES["age"]))
        elif intent == "math":
            a, op, b = captures.get("math")
            try:
                a = float(a); b = float(b)
                if op == "+":
                    val = a + b
                elif op == "-":
                    val = a - b
                elif op == "*":
                    val = a * b
                elif op == "/":
                    val = a / b if b != 0 else "Infinity"
                out_responses.append(f"The answer is {val}")
            except Exception:
                out_responses.append("I couldn't compute that math expression.")
        else:
            out_responses.append(random.choice(RESPONSES["unknown"]))

    return " ".join(out_responses)

def main():
    print("ChatBot v1.0 — type 'exit' or 'quit' to leave.")
    state = {"should_exit": False, "user_name": None}

    while True:
        user = input("You: ")
        if not user.strip():
            print("Bot: Please say something or type 'help'.")
            continue

        # quick exit check (exact words)
        if user.strip().lower() in EXIT_KEYWORDS:
            print("Bot:", random.choice(RESPONSES["bye"]))
            break

        text = preprocess(user)
        intents, captures = find_intents(text)

        response = handle_intents(intents, captures, state)
        print("Bot:", response)

        if state.get("should_exit"):
            break

if __name__ == "__main__":
    main()
