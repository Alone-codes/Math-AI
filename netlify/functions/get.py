import json
import nltk
from nltk.chat.util import Chat, reflections
import re
import ast

nltk.download('punkt')

# Define chat pairs with improved acknowledgment handling
pairs = [
    # Greetings
    (r'Hi|Hello|Hey', ['Hello!', 'Hi there!', 'Hey! How can I help you?']),
    
    # Identity
    (r'Who are you|What is your name', ['I am a chatbot created by Vishwa.', 'You can call me Vishwa.']),
    
    # Feelings
    (r'How are you', ['I am good, thank you for asking! How about you and your family?', 
                     'Ohh really you care about me, thank you! I am good. How about you and your family?']),
    
    # Purpose
    (r'What are your uses|Why are you here', [
        "I'm here to chat and assist you with whatever you need!",
        "I can help with math, information, and even tell jokes!"
    ]),
    
    # Jokes
    (r'Tell me a joke|Tell me something funny|joke', [
        "Why don't skeletons fight each other? They don't have the guts!",
        "Why don't some couples go to the gym? Because some relationships don't work out!",
    ]),
    
    # Personal questions
    (r'(.*) your (.*)', ['Please don\'t ask about my personal things, I\'m too shy for that.']),
    
    # Relationship questions
    (r'Are you single|I love you', ["No, I'm in a relationship with my code!!!!!!!"]),
    
    # Goodbyes
    (r'quit|bye|tata', ['Bye! Take care!', 'Goodbye! It was nice chatting with you.']),
    
    # Math - handled separately in the route
    
    # Improved acknowledgment patterns
    (r'(?i)^ok(ay)?$', ['Okay!', 'Got it!']),
    (r'(?i)^thanks?$', ['You\'re welcome!', 'No problem!']),
    (r'(?i)^ok(ay)? thanks?$', ['You\'re welcome!', 'No problem!']),
    (r'(?i)^thanks? ok(ay)?$', ['You\'re welcome!', 'No problem!']),
    
    # Catch-all for unmatched inputs
    (r'.*', ["I'm not sure I understand. Could you rephrase that?"])
]

chatbot = Chat(pairs, reflections)

def evaluate_math_expression(expression):
    """Safely evaluate math expressions"""
    expression = expression.replace(' ', '')
    
    # More thorough validation
    if not re.match(r'^[\d+\-*/().\s]+$', expression):
        return "Please enter a valid math expression with numbers and +-*/() only."
    
    try:
        # Safer alternative to eval()
        tree = ast.parse(expression, mode='eval')
        if not all(isinstance(node, (ast.Constant, ast.UnaryOp, ast.BinOp)) for node in ast.walk(tree)):
            raise ValueError("Unsafe expression")
        result = eval(compile(tree, filename='', mode='eval'), {'__builtins__': None})
        return f"The result is: {result}"
    except Exception:
        return "Sorry, I couldn't evaluate that. Please check your expression."

def handler(event, context):
    if event['httpMethod'] != 'GET':
        return {
            'statusCode': 405,
            'body': json.dumps({'error': 'Method not allowed'})
        }
    
    query_params = event.get('queryStringParameters') or {}
    user_message = query_params.get('msg', '').strip()
    
    # Check for math expressions first
    if any(op in user_message for op in ['+', '-', '*', '/', '(', ')']):
        response = evaluate_math_expression(user_message)
    else:
        # Get chatbot response
        response = chatbot.respond(user_message)
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'GET, OPTIONS'
        },
        'body': json.dumps({"response": response})
    }