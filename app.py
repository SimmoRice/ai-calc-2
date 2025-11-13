"""
macOS-themed Web Calculator with Flask
Supports basic arithmetic operations, light/dark themes, and calculation history
"""
from flask import Flask, render_template, request, jsonify, session
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman
import secrets
import re
import ast
import operator
from collections import deque

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# SECURITY: Configure session cookie security
app.config.update(
    SESSION_COOKIE_SECURE=False,  # Set to True when using HTTPS in production
    SESSION_COOKIE_HTTPONLY=True,  # Prevent JavaScript access to session cookie
    SESSION_COOKIE_SAMESITE='Lax',  # CSRF protection via SameSite attribute
    PERMANENT_SESSION_LIFETIME=3600  # Session expires after 1 hour
)

# SECURITY: Configure rate limiting to prevent abuse
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

# SECURITY: Configure security headers (Talisman)
# Allow inline scripts for calculator functionality with nonce
csp = {
    'default-src': "'self'",
    'script-src': ["'self'", "'unsafe-inline'"],  # Needed for inline event handlers
    'style-src': ["'self'", "'unsafe-inline'"],   # Needed for inline styles
    'img-src': "'self'",
}
Talisman(app,
         content_security_policy=csp,
         force_https=False)  # Set to True in production with HTTPS

# Store calculation history in session (max 5)
MAX_HISTORY = 5

# SECURITY: Safe mathematical operators for expression evaluation
# Only allow basic arithmetic operations - no dangerous functions
SAFE_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.USub: operator.neg,  # Unary minus
    ast.UAdd: operator.pos,  # Unary plus
}


def safe_eval(expression):
    """
    SECURITY: Safely evaluate mathematical expressions using AST parsing
    This replaces the dangerous eval() function with a whitelist approach
    Only allows basic arithmetic operations, prevents code injection
    """
    try:
        # Parse the expression into an Abstract Syntax Tree
        tree = ast.parse(expression, mode='eval')

        # Validate that only safe operations are used
        def validate_node(node):
            if isinstance(node, ast.Expression):
                return validate_node(node.body)
            elif isinstance(node, ast.BinOp):
                if type(node.op) not in SAFE_OPERATORS:
                    raise ValueError(f"Unsafe operation: {type(node.op).__name__}")
                validate_node(node.left)
                validate_node(node.right)
            elif isinstance(node, ast.UnaryOp):
                if type(node.op) not in SAFE_OPERATORS:
                    raise ValueError(f"Unsafe operation: {type(node.op).__name__}")
                validate_node(node.operand)
            elif isinstance(node, (ast.Constant, ast.Num)):
                # Numbers are safe
                pass
            else:
                raise ValueError(f"Unsafe node type: {type(node).__name__}")

        validate_node(tree)

        # Evaluate the validated AST
        def eval_node(node):
            if isinstance(node, ast.Expression):
                return eval_node(node.body)
            elif isinstance(node, ast.BinOp):
                left = eval_node(node.left)
                right = eval_node(node.right)
                return SAFE_OPERATORS[type(node.op)](left, right)
            elif isinstance(node, ast.UnaryOp):
                operand = eval_node(node.operand)
                return SAFE_OPERATORS[type(node.op)](operand)
            elif isinstance(node, ast.Constant):  # Python 3.8+
                return node.value
            elif isinstance(node, ast.Num):  # Python 3.7 and earlier
                return node.n
            else:
                raise ValueError(f"Unsupported node type: {type(node).__name__}")

        return eval_node(tree)

    except (SyntaxError, ValueError) as e:
        raise ValueError(f"Invalid expression: {str(e)}")


@app.route('/')
def index():
    """Render the calculator interface"""
    return render_template('index.html')


@app.route('/calculate', methods=['POST'])
@limiter.limit("30 per minute")  # SECURITY: Rate limit calculation endpoint
def calculate():
    """
    Process calculation request and return result
    Maintains history of last 5 calculations
    """
    try:
        data = request.get_json()

        # SECURITY: Validate JSON data exists
        if not data:
            return jsonify({'error': 'Invalid request'}), 400

        expression = data.get('expression', '')

        # SECURITY: Validate expression length to prevent abuse
        if len(expression) > 200:
            return jsonify({'error': 'Expression too long'}), 400

        # SECURITY: Validate expression (only allow safe characters)
        # This is a first-line defense; safe_eval provides deeper protection
        allowed_chars = set('0123456789+-*/(). ')
        if not all(c in allowed_chars for c in expression):
            return jsonify({'error': 'Invalid characters in expression'}), 400

        # SECURITY: Use safe_eval instead of dangerous eval()
        # This prevents code injection attacks
        result = safe_eval(expression)

        # Initialize history if not exists
        if 'history' not in session:
            session['history'] = []

        # SECURITY: Validate history is a list
        history = session.get('history', [])
        if not isinstance(history, list):
            history = []

        # Add to history (keep last 5)
        history.append({
            'expression': expression,
            'result': result
        })

        # Keep only last 5 calculations
        if len(history) > MAX_HISTORY:
            history = history[-MAX_HISTORY:]

        session['history'] = history
        session.modified = True

        return jsonify({
            'result': result,
            'history': history
        })

    except ZeroDivisionError:
        # SECURITY: Don't expose internal error details
        return jsonify({'error': 'Division by zero'}), 400
    except ValueError as e:
        # SECURITY: Safe to show validation errors (no stack trace)
        return jsonify({'error': 'Invalid expression'}), 400
    except Exception as e:
        # SECURITY: Generic error message - don't leak internal details
        # Log the actual error for debugging (in production, use proper logging)
        app.logger.error(f"Calculation error: {str(e)}")
        return jsonify({'error': 'Calculation failed'}), 400


@app.route('/history', methods=['GET'])
@limiter.limit("60 per minute")  # SECURITY: Rate limit history endpoint
def get_history():
    """Return calculation history"""
    # SECURITY: Validate history data type
    history = session.get('history', [])
    if not isinstance(history, list):
        history = []
        session['history'] = history
    return jsonify({'history': history})


@app.route('/clear-history', methods=['POST'])
@limiter.limit("20 per minute")  # SECURITY: Rate limit clear endpoint
def clear_history():
    """Clear calculation history"""
    session['history'] = []
    session.modified = True
    return jsonify({'success': True})


# SECURITY: Additional headers for defense in depth
@app.after_request
def set_security_headers(response):
    """Set additional security headers on all responses"""
    # Prevent MIME type sniffing
    response.headers['X-Content-Type-Options'] = 'nosniff'
    # Enable XSS filter in browsers
    response.headers['X-XSS-Protection'] = '1; mode=block'
    # Control referrer information
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    # Prevent clickjacking (already handled by Talisman but added for redundancy)
    response.headers['X-Frame-Options'] = 'DENY'
    return response


if __name__ == '__main__':
    # SECURITY: Disable debug mode in production!
    # Debug mode exposes sensitive information and the debugger console
    import os
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'

    if debug_mode:
        app.logger.warning("⚠️  WARNING: Running in DEBUG mode - DO NOT use in production!")

    app.run(debug=debug_mode, host='0.0.0.0', port=5000)
