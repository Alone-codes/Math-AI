from flask import Flask, render_template, request, jsonify
import nltk
from nltk.chat.util import Chat, reflections
import re
import ast  # For safer math evaluation
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
    # (r'(.*) your (.*)', ['Please don't ask about my personal things, I'm too shy for that.']),
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

app = Flask(__name__)

def validate_math_ast(node):
    if isinstance(node, ast.BinOp):
        if not isinstance(node.op, (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Mod, ast.Pow, ast.FloorDiv)):
            return False
        return validate_math_ast(node.left) and validate_math_ast(node.right)
    elif isinstance(node, ast.UnaryOp):
        if not isinstance(node.op, (ast.UAdd, ast.USub)):
            return False
        return validate_math_ast(node.operand)
    elif isinstance(node, ast.Constant):
        return isinstance(node.value, (int, float, complex))
    elif hasattr(ast, 'Num') and isinstance(node, ast.Num):
        return isinstance(node.n, (int, float, complex))
    else:
        return False

def evaluate_math_expression(expression):
    """Safely evaluate math expressions"""
    expression = expression.replace(' ', '')
    
    # More thorough validation
    if not re.match(r'^[\d+\-*/().\s]+$', expression):
        return "Please enter a valid math expression with numbers and +-*/() only."
    
    try:
        # Safer alternative to eval()
        tree = ast.parse(expression, mode='eval')
        if not validate_math_ast(tree.body):
            raise ValueError("Unsafe expression")
        result = eval(compile(tree, filename='', mode='eval'), {'__builtins__': None})
        return f"The result is: {result}"
    except Exception:
        return "Sorry, I couldn't evaluate that. Please check your expression."

@app.route('/')
def index():
    return render_template('index.html')
    
@app.route('/get', methods=['GET'])
def get_bot_response():
    user_message = request.args.get('msg', '').strip()
    
    # Debug prints (remove in production)
    print(f"User message: '{user_message}'")
    
    # Check for math expressions first
    if any(op in user_message for op in ['+', '-', '*', '/', '(', ')']):
        return jsonify({"response": evaluate_math_expression(user_message)})
    
    # Get chatbot response
    response = chatbot.respond(user_message)
    print(f"Chatbot response: '{response}'")  # Debug
    
    return jsonify({"response": response})

if __name__ == '__main__':
    app.run(debug=True)
