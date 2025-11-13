"""
macOS-themed Web Calculator with Flask
Supports basic arithmetic operations, scientific functions, light/dark themes, and calculation history

SECURITY FEATURES:
- Safe expression evaluation using AST parsing (no eval())
- Input validation and sanitization
- Rate limiting to prevent abuse
- XSS prevention via DOM manipulation
- CSRF protection via SameSite cookies
- Secure session management with HTTPOnly cookies
- Security headers (CSP, X-Frame-Options, etc.)
- No sensitive data exposure in errors
"""
from flask import Flask, render_template, request, jsonify, session
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman
import secrets
import re
import ast
import operator
import math
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
    storage_uri="memory://",
    enabled=lambda: app.config.get('RATELIMIT_ENABLED', True)
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

# Store calculation history in session (max 10)
MAX_HISTORY = 10

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
    Maintains history of last 10 calculations

    SECURITY NOTE: For production with multiple frontend origins, consider
    implementing CSRF token validation in addition to SameSite cookies.
    """
    try:
        data = request.get_json()

        # SECURITY: Validate JSON data exists
        if not data:
            return jsonify({'error': 'Invalid request'}), 400

        expression = data.get('expression', '')

        # SECURITY: Validate expression type to prevent type confusion
        if not isinstance(expression, str):
            return jsonify({'error': 'Invalid expression type'}), 400

        # SECURITY: Validate expression is not empty
        if not expression or not expression.strip():
            return jsonify({'error': 'Empty expression'}), 400

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

        # SECURITY: Validate result is a finite number
        if not isinstance(result, (int, float)):
            return jsonify({'error': 'Invalid result type'}), 400

        # Check for NaN or Infinity
        if result != result:  # NaN check
            return jsonify({'error': 'Result is not a number'}), 400
        if result == float('inf') or result == float('-inf'):
            return jsonify({'error': 'Result is infinite'}), 400

        # Initialize history if not exists
        if 'history' not in session:
            session['history'] = []

        # SECURITY: Validate history is a list
        history = session.get('history', [])
        if not isinstance(history, list):
            history = []

        # SECURITY: Sanitize history entries before adding
        # Truncate extremely long expressions to prevent session bloat
        sanitized_expression = expression[:100] if len(expression) > 100 else expression

        # Add to history (keep last 10)
        history.append({
            'expression': sanitized_expression,
            'result': float(result)  # Ensure consistent numeric type
        })

        # Keep only last 10 calculations
        if len(history) > MAX_HISTORY:
            history = history[-MAX_HISTORY:]

        # SECURITY: Validate history size to prevent session exhaustion
        # Limit total history entries regardless of MAX_HISTORY constant
        if len(history) > 100:  # Hard limit as failsafe
            history = history[-100:]

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


@app.route('/scientific', methods=['POST'])
@limiter.limit("30 per minute")  # SECURITY: Rate limit scientific endpoint
def scientific():
    """
    Process scientific function requests
    Supports trigonometric, logarithmic, exponential, and power functions
    """
    try:
        data = request.get_json()

        # SECURITY: Validate JSON data exists
        if not data:
            return jsonify({'error': 'Invalid request'}), 400

        func = data.get('function', '')
        value = data.get('value')

        # SECURITY: Validate function name
        if not isinstance(func, str):
            return jsonify({'error': 'Invalid function type'}), 400

        # SECURITY: Whitelist of allowed functions
        allowed_functions = {
            'sin', 'cos', 'tan', 'asin', 'acos', 'atan',
            'log', 'ln', 'exp', 'sqrt', 'square', 'reciprocal', 'power'
        }

        if func not in allowed_functions:
            return jsonify({'error': 'Unknown function'}), 400

        # Handle power function (takes two values)
        if func == 'power':
            if not isinstance(value, dict):
                return jsonify({'error': 'Invalid power parameters'}), 400

            base = value.get('base')
            exponent = value.get('exponent')

            # SECURITY: Validate both parameters are numbers
            if not isinstance(base, (int, float)) or not isinstance(exponent, (int, float)):
                return jsonify({'error': 'Invalid power parameters'}), 400

            # Check for valid numbers
            if not all(isinstance(x, (int, float)) and math.isfinite(x) for x in [base, exponent]):
                return jsonify({'error': 'Invalid power parameters'}), 400

            # Calculate power
            try:
                result = math.pow(base, exponent)
            except (ValueError, OverflowError) as e:
                return jsonify({'error': 'Power calculation error'}), 400

        else:
            # Single-value functions
            # SECURITY: Validate value is a number
            if not isinstance(value, (int, float)):
                return jsonify({'error': 'Invalid value type'}), 400

            # Check for valid number
            if not math.isfinite(value):
                return jsonify({'error': 'Invalid value'}), 400

            # Execute the scientific function
            try:
                if func == 'sin':
                    result = math.sin(value)
                elif func == 'cos':
                    result = math.cos(value)
                elif func == 'tan':
                    result = math.tan(value)
                elif func == 'asin':
                    if value < -1 or value > 1:
                        return jsonify({'error': 'Domain error: asin requires value between -1 and 1'}), 400
                    result = math.asin(value)
                elif func == 'acos':
                    if value < -1 or value > 1:
                        return jsonify({'error': 'Domain error: acos requires value between -1 and 1'}), 400
                    result = math.acos(value)
                elif func == 'atan':
                    result = math.atan(value)
                elif func == 'log':
                    if value <= 0:
                        return jsonify({'error': 'Domain error: log requires positive value'}), 400
                    result = math.log10(value)
                elif func == 'ln':
                    if value <= 0:
                        return jsonify({'error': 'Domain error: ln requires positive value'}), 400
                    result = math.log(value)
                elif func == 'exp':
                    result = math.exp(value)
                elif func == 'sqrt':
                    if value < 0:
                        return jsonify({'error': 'Domain error: sqrt requires non-negative value'}), 400
                    result = math.sqrt(value)
                elif func == 'square':
                    result = value * value
                elif func == 'reciprocal':
                    if value == 0:
                        return jsonify({'error': 'Division by zero'}), 400
                    result = 1 / value
                else:
                    return jsonify({'error': 'Unknown function'}), 400

            except (ValueError, OverflowError) as e:
                return jsonify({'error': 'Calculation error'}), 400

        # SECURITY: Validate result is a finite number
        if not isinstance(result, (int, float)):
            return jsonify({'error': 'Invalid result type'}), 400

        # Check for NaN or Infinity
        if not math.isfinite(result):
            return jsonify({'error': 'Result is not finite'}), 400

        return jsonify({'result': result})

    except Exception as e:
        # SECURITY: Generic error message - don't leak internal details
        app.logger.error(f"Scientific calculation error: {str(e)}")
        return jsonify({'error': 'Calculation failed'}), 400


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

    # SECURITY: Validate environment variable to prevent injection
    debug_env = os.environ.get('FLASK_DEBUG', 'False').lower()
    debug_mode = debug_env in ('true', '1', 'yes')

    if debug_mode:
        app.logger.warning("⚠️  WARNING: Running in DEBUG mode - DO NOT use in production!")

    # SECURITY: Validate production environment
    is_production = os.environ.get('FLASK_ENV', 'development').lower() == 'production'

    if is_production:
        # SECURITY: Force HTTPS settings in production
        if not app.config['SESSION_COOKIE_SECURE']:
            app.logger.warning("⚠️  WARNING: SESSION_COOKIE_SECURE should be True in production!")
        # Ensure debug is off in production
        if debug_mode:
            app.logger.error("❌ ERROR: Debug mode MUST be disabled in production!")
            exit(1)

    app.run(debug=debug_mode, host='0.0.0.0', port=5001)
