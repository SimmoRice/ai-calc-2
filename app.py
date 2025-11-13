"""
macOS-themed Web Calculator with Flask
Supports basic arithmetic operations, light/dark themes, and calculation history
"""
from flask import Flask, render_template, request, jsonify, session
import secrets
from collections import deque

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Store calculation history in session (max 5)
MAX_HISTORY = 5


@app.route('/')
def index():
    """Render the calculator interface"""
    return render_template('index.html')


@app.route('/calculate', methods=['POST'])
def calculate():
    """
    Process calculation request and return result
    Maintains history of last 5 calculations
    """
    try:
        data = request.get_json()
        expression = data.get('expression', '')

        # Validate expression (only allow safe characters)
        allowed_chars = set('0123456789+-*/(). ')
        if not all(c in allowed_chars for c in expression):
            return jsonify({'error': 'Invalid characters in expression'}), 400

        # Calculate result
        result = eval(expression)

        # Initialize history if not exists
        if 'history' not in session:
            session['history'] = []

        # Add to history (keep last 5)
        history = session['history']
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
        return jsonify({'error': 'Division by zero'}), 400
    except Exception as e:
        return jsonify({'error': 'Invalid expression'}), 400


@app.route('/history', methods=['GET'])
def get_history():
    """Return calculation history"""
    history = session.get('history', [])
    return jsonify({'history': history})


@app.route('/clear-history', methods=['POST'])
def clear_history():
    """Clear calculation history"""
    session['history'] = []
    session.modified = True
    return jsonify({'success': True})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
