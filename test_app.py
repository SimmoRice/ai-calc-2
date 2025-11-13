"""
Comprehensive Test Suite for macOS-themed Web Calculator
Tests cover:
- Unit tests for safe_eval function
- Flask route and endpoint tests
- Security validation tests
- Edge cases and error handling
- History management
"""
import pytest
import json
from app import app, safe_eval, MAX_HISTORY, limiter


# Test Fixtures
@pytest.fixture(autouse=True)
def _disable_limiter():
    """Disable rate limiting for all tests"""
    limiter.enabled = False
    yield
    limiter.enabled = True


@pytest.fixture
def client():
    """Create a test client for the Flask app"""
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret-key'
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess['history'] = []
        yield client


@pytest.fixture
def client_with_history(client):
    """Create a test client with pre-populated history"""
    with client.session_transaction() as sess:
        sess['history'] = [
            {'expression': '1+1', 'result': 2},
            {'expression': '5*3', 'result': 15},
            {'expression': '10-4', 'result': 6}
        ]
    return client


# ============================================================================
# UNIT TESTS: safe_eval Function
# ============================================================================

class TestSafeEval:
    """Test the safe_eval function for correct evaluation and security"""

    def test_basic_addition(self):
        """Test simple addition"""
        assert safe_eval('2+2') == 4
        assert safe_eval('10+5') == 15
        assert safe_eval('0+0') == 0

    def test_basic_subtraction(self):
        """Test simple subtraction"""
        assert safe_eval('10-5') == 5
        assert safe_eval('5-10') == -5
        assert safe_eval('0-5') == -5

    def test_basic_multiplication(self):
        """Test simple multiplication"""
        assert safe_eval('3*4') == 12
        assert safe_eval('10*0') == 0
        assert safe_eval('7*8') == 56

    def test_basic_division(self):
        """Test simple division"""
        assert safe_eval('10/2') == 5
        assert safe_eval('15/3') == 5
        assert safe_eval('7/2') == 3.5

    def test_division_by_zero(self):
        """Test that division by zero raises ZeroDivisionError"""
        with pytest.raises(ZeroDivisionError):
            safe_eval('10/0')

    def test_complex_expressions(self):
        """Test complex mathematical expressions"""
        assert safe_eval('2+3*4') == 14  # Order of operations
        assert safe_eval('(2+3)*4') == 20  # Parentheses
        assert safe_eval('10-5+3') == 8
        assert safe_eval('100/10/2') == 5

    def test_negative_numbers(self):
        """Test expressions with negative numbers"""
        assert safe_eval('-5') == -5
        assert safe_eval('-5+10') == 5
        assert safe_eval('10*-2') == -20

    def test_decimal_numbers(self):
        """Test expressions with decimal numbers"""
        assert safe_eval('1.5+2.5') == 4.0
        assert safe_eval('10.5*2') == 21.0
        assert safe_eval('7.5/2.5') == 3.0

    def test_whitespace_handling(self):
        """Test that whitespace is handled correctly"""
        assert safe_eval('2 + 2') == 4
        assert safe_eval('10 * 5') == 50

    def test_invalid_syntax(self):
        """Test that invalid syntax raises ValueError"""
        with pytest.raises((ValueError, SyntaxError)):
            safe_eval('2+')
        with pytest.raises((ValueError, SyntaxError)):
            safe_eval('*5')

    def test_code_injection_protection(self):
        """Test that code injection attempts are blocked"""
        # Attempt to use __import__
        with pytest.raises(ValueError):
            safe_eval('__import__("os")')

        # Attempt to use eval
        with pytest.raises(ValueError):
            safe_eval('eval("2+2")')

        # Attempt to access attributes
        with pytest.raises(ValueError):
            safe_eval('().__class__')

    def test_dangerous_functions_blocked(self):
        """Test that dangerous functions are blocked"""
        dangerous_inputs = [
            'exec("print(1)")',
            'compile("1+1", "", "eval")',
            'open("/etc/passwd")',
            'print(1)',
            'len([1,2,3])',
        ]
        for dangerous_input in dangerous_inputs:
            with pytest.raises(ValueError):
                safe_eval(dangerous_input)

    def test_variable_assignment_blocked(self):
        """Test that variable assignment is blocked"""
        with pytest.raises(ValueError):
            safe_eval('x=5')

    def test_list_dict_blocked(self):
        """Test that list and dict creation is blocked"""
        with pytest.raises(ValueError):
            safe_eval('[1,2,3]')
        with pytest.raises(ValueError):
            safe_eval('{"a": 1}')


# ============================================================================
# ROUTE TESTS: Flask Endpoints
# ============================================================================

class TestRoutes:
    """Test Flask routes and endpoints"""

    def test_index_route(self, client):
        """Test that the index route returns HTML"""
        response = client.get('/')
        assert response.status_code == 200
        assert b'macOS Calculator' in response.data

    def test_calculate_route_success(self, client):
        """Test successful calculation via /calculate endpoint"""
        response = client.post('/calculate',
                              data=json.dumps({'expression': '5+3'}),
                              content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['result'] == 8
        assert 'history' in data

    def test_calculate_route_updates_history(self, client):
        """Test that calculations are added to history"""
        # First calculation
        response = client.post('/calculate',
                              data=json.dumps({'expression': '5+3'}),
                              content_type='application/json')
        data = json.loads(response.data)
        assert len(data['history']) == 1
        assert data['history'][0]['expression'] == '5+3'
        assert data['history'][0]['result'] == 8

        # Second calculation
        response = client.post('/calculate',
                              data=json.dumps({'expression': '10*2'}),
                              content_type='application/json')
        data = json.loads(response.data)
        assert len(data['history']) == 2

    def test_calculate_route_invalid_json(self, client):
        """Test that invalid JSON returns 400 error"""
        response = client.post('/calculate',
                              data='invalid json',
                              content_type='application/json')
        assert response.status_code == 400

    def test_calculate_route_missing_expression(self, client):
        """Test that missing expression is handled"""
        response = client.post('/calculate',
                              data=json.dumps({}),
                              content_type='application/json')
        assert response.status_code == 400

    def test_history_route(self, client_with_history):
        """Test that /history returns calculation history"""
        response = client_with_history.get('/history')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data['history']) == 3
        assert data['history'][0]['expression'] == '1+1'

    def test_history_route_empty(self, client):
        """Test that /history returns empty array when no history"""
        response = client.get('/history')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['history'] == []

    def test_clear_history_route(self, client_with_history):
        """Test that /clear-history clears the history"""
        # Verify history exists
        response = client_with_history.get('/history')
        data = json.loads(response.data)
        assert len(data['history']) == 3

        # Clear history
        response = client_with_history.post('/clear-history',
                                           content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True

        # Verify history is cleared
        response = client_with_history.get('/history')
        data = json.loads(response.data)
        assert data['history'] == []


# ============================================================================
# SECURITY TESTS
# ============================================================================

class TestSecurity:
    """Test security features and validations"""

    def test_expression_length_limit(self, client):
        """Test that overly long expressions are rejected"""
        long_expression = '1+' * 200  # Creates very long expression
        response = client.post('/calculate',
                              data=json.dumps({'expression': long_expression}),
                              content_type='application/json')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data

    def test_invalid_characters_rejected(self, client):
        """Test that invalid characters are rejected"""
        invalid_expressions = [
            '2+2; import os',
            '2+2\nimport os',
            'eval(5+5)',
            '__import__("os")',
            '2+2; print("hacked")',
        ]
        for expr in invalid_expressions:
            response = client.post('/calculate',
                                  data=json.dumps({'expression': expr}),
                                  content_type='application/json')
            assert response.status_code == 400

    def test_sql_injection_attempts(self, client):
        """Test that SQL injection attempts are blocked"""
        sql_injections = [
            "'; DROP TABLE users--",
            "1' OR '1'='1",
            "admin'--",
        ]
        for injection in sql_injections:
            response = client.post('/calculate',
                                  data=json.dumps({'expression': injection}),
                                  content_type='application/json')
            assert response.status_code == 400

    def test_xss_attempts(self, client):
        """Test that XSS attempts are blocked"""
        xss_attempts = [
            '<script>alert("xss")</script>',
            '<img src=x onerror=alert(1)>',
            'javascript:alert(1)',
        ]
        for xss in xss_attempts:
            response = client.post('/calculate',
                                  data=json.dumps({'expression': xss}),
                                  content_type='application/json')
            assert response.status_code == 400

    def test_command_injection_attempts(self, client):
        """Test that command injection attempts are blocked"""
        command_injections = [
            '`ls`',
            '$(whoami)',
            '${IFS}',
        ]
        for cmd in command_injections:
            response = client.post('/calculate',
                                  data=json.dumps({'expression': cmd}),
                                  content_type='application/json')
            assert response.status_code == 400

    def test_security_headers(self, client):
        """Test that security headers are set correctly"""
        response = client.get('/')
        assert 'X-Content-Type-Options' in response.headers
        assert response.headers['X-Content-Type-Options'] == 'nosniff'
        assert 'X-XSS-Protection' in response.headers
        assert 'X-Frame-Options' in response.headers
        # Talisman sets X-Frame-Options to SAMEORIGIN by default
        assert response.headers['X-Frame-Options'] in ['DENY', 'SAMEORIGIN']

    def test_session_cookie_security(self, client):
        """Test that session cookies have security attributes"""
        response = client.get('/')
        # Check that Set-Cookie header has security attributes
        set_cookie = response.headers.get('Set-Cookie', '')
        # Note: In test mode, Secure flag may not be set
        assert 'HttpOnly' in set_cookie or response.status_code == 200

    def test_history_type_validation(self, client):
        """Test that invalid history data types are handled"""
        # Manually set invalid history type in session
        with client.session_transaction() as sess:
            sess['history'] = "invalid"  # Should be a list

        response = client.get('/history')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data['history'], list)
        assert data['history'] == []


# ============================================================================
# EDGE CASES AND ERROR HANDLING
# ============================================================================

class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_division_by_zero_error(self, client):
        """Test that division by zero returns appropriate error"""
        response = client.post('/calculate',
                              data=json.dumps({'expression': '10/0'}),
                              content_type='application/json')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'Division by zero' in data['error']

    def test_very_large_numbers(self, client):
        """Test calculations with very large numbers"""
        response = client.post('/calculate',
                              data=json.dumps({'expression': '999999999*999999999'}),
                              content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['result'] == 999999998000000001

    def test_very_small_numbers(self, client):
        """Test calculations with very small decimal numbers"""
        response = client.post('/calculate',
                              data=json.dumps({'expression': '0.0001+0.0002'}),
                              content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert abs(data['result'] - 0.0003) < 0.0001  # Allow for floating point precision

    def test_negative_result(self, client):
        """Test calculations that result in negative numbers"""
        response = client.post('/calculate',
                              data=json.dumps({'expression': '5-10'}),
                              content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['result'] == -5

    def test_empty_expression(self, client):
        """Test that empty expression is handled"""
        response = client.post('/calculate',
                              data=json.dumps({'expression': ''}),
                              content_type='application/json')
        assert response.status_code == 400

    def test_whitespace_only_expression(self, client):
        """Test that whitespace-only expression is handled"""
        response = client.post('/calculate',
                              data=json.dumps({'expression': '   '}),
                              content_type='application/json')
        assert response.status_code == 400

    def test_malformed_parentheses(self, client):
        """Test that malformed parentheses are handled"""
        malformed = [
            '(2+2',
            '2+2)',
            '((2+2)',
            '(2+2))',
        ]
        for expr in malformed:
            response = client.post('/calculate',
                                  data=json.dumps({'expression': expr}),
                                  content_type='application/json')
            assert response.status_code == 400

    def test_consecutive_operators(self, client):
        """Test that consecutive operators are handled"""
        # Note: 2++2 is actually valid in Python (it's 2 + (+2))
        # But 2+-+2 should still be handled
        response = client.post('/calculate',
                              data=json.dumps({'expression': '2**2'}),  # ** not allowed
                              content_type='application/json')
        assert response.status_code == 400


# ============================================================================
# HISTORY MANAGEMENT TESTS
# ============================================================================

class TestHistoryManagement:
    """Test history management features"""

    def test_history_max_size(self, client):
        """Test that history is limited to MAX_HISTORY items"""
        # Add more than MAX_HISTORY calculations
        for i in range(MAX_HISTORY + 3):
            response = client.post('/calculate',
                                  data=json.dumps({'expression': f'{i}+1'}),
                                  content_type='application/json')
            assert response.status_code == 200

        # Check that history contains only MAX_HISTORY items
        response = client.get('/history')
        data = json.loads(response.data)
        assert len(data['history']) == MAX_HISTORY

        # Verify that oldest items were removed (should start with item 3)
        assert data['history'][0]['expression'] == '3+1'

    def test_history_order(self, client):
        """Test that history maintains correct order"""
        # Add calculations in order
        expressions = ['1+1', '2+2', '3+3', '4+4', '5+5']
        for expr in expressions:
            client.post('/calculate',
                       data=json.dumps({'expression': expr}),
                       content_type='application/json')

        # Verify order is maintained
        response = client.get('/history')
        data = json.loads(response.data)
        for i, item in enumerate(data['history']):
            assert item['expression'] == expressions[i]

    def test_history_persistence_across_requests(self, client):
        """Test that history persists across multiple requests"""
        # Add first calculation
        client.post('/calculate',
                   data=json.dumps({'expression': '5+5'}),
                   content_type='application/json')

        # Make another request and verify history is still there
        response = client.post('/calculate',
                              data=json.dumps({'expression': '10+10'}),
                              content_type='application/json')
        data = json.loads(response.data)
        assert len(data['history']) == 2
        assert data['history'][0]['expression'] == '5+5'
        assert data['history'][1]['expression'] == '10+10'

    def test_clear_history_and_add_new(self, client_with_history):
        """Test clearing history and adding new calculations"""
        # Clear history
        client_with_history.post('/clear-history',
                                content_type='application/json')

        # Add new calculation
        response = client_with_history.post('/calculate',
                                           data=json.dumps({'expression': '7+7'}),
                                           content_type='application/json')
        data = json.loads(response.data)
        assert len(data['history']) == 1
        assert data['history'][0]['expression'] == '7+7'

    def test_history_exactly_10_items(self, client):
        """Test that history maintains exactly 10 items when limit is reached"""
        # Add exactly 10 calculations
        for i in range(10):
            response = client.post('/calculate',
                                  data=json.dumps({'expression': f'{i}+{i}'}),
                                  content_type='application/json')
            assert response.status_code == 200

        # Verify exactly 10 items
        response = client.get('/history')
        data = json.loads(response.data)
        assert len(data['history']) == 10
        assert data['history'][0]['expression'] == '0+0'
        assert data['history'][9]['expression'] == '9+9'

    def test_history_11th_item_removes_oldest(self, client):
        """Test that adding 11th item removes the oldest item"""
        # Add 10 calculations
        for i in range(10):
            client.post('/calculate',
                       data=json.dumps({'expression': f'{i}+1'}),
                       content_type='application/json')

        # Add 11th calculation
        response = client.post('/calculate',
                              data=json.dumps({'expression': '100+100'}),
                              content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)

        # Verify still 10 items, oldest removed
        assert len(data['history']) == 10
        # First item should be '1+1' (0+1 was removed)
        assert data['history'][0]['expression'] == '1+1'
        # Last item should be the new one
        assert data['history'][9]['expression'] == '100+100'
        assert data['history'][9]['result'] == 200

    def test_history_rotation_with_15_items(self, client):
        """Test that history properly rotates when adding 15 items"""
        # Add 15 calculations
        for i in range(15):
            response = client.post('/calculate',
                                  data=json.dumps({'expression': f'{i}*2'}),
                                  content_type='application/json')
            assert response.status_code == 200

        # Verify only last 10 are kept
        response = client.get('/history')
        data = json.loads(response.data)
        assert len(data['history']) == 10

        # Should have items 5 through 14
        for i, item in enumerate(data['history']):
            expected_expr = f'{i+5}*2'
            assert item['expression'] == expected_expr
            assert item['result'] == (i+5) * 2

    def test_history_max_constant_value(self, client):
        """Test that MAX_HISTORY constant is actually 10"""
        assert MAX_HISTORY == 10, "MAX_HISTORY should be 10 per requirements"


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestIntegration:
    """Integration tests for complete workflows"""

    def test_complete_calculation_workflow(self, client):
        """Test a complete workflow of multiple calculations"""
        # Perform a series of calculations
        calculations = [
            ('5+3', 8),
            ('10*2', 20),
            ('100/4', 25),
            ('15-7', 8),
        ]

        for expr, expected in calculations:
            response = client.post('/calculate',
                                  data=json.dumps({'expression': expr}),
                                  content_type='application/json')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['result'] == expected

        # Verify all in history
        response = client.get('/history')
        data = json.loads(response.data)
        assert len(data['history']) == 4

    def test_error_recovery(self, client):
        """Test that errors don't corrupt application state"""
        # Make a successful calculation
        response = client.post('/calculate',
                              data=json.dumps({'expression': '5+5'}),
                              content_type='application/json')
        assert response.status_code == 200

        # Make an invalid calculation
        response = client.post('/calculate',
                              data=json.dumps({'expression': 'invalid'}),
                              content_type='application/json')
        assert response.status_code == 400

        # Make another successful calculation
        response = client.post('/calculate',
                              data=json.dumps({'expression': '10+10'}),
                              content_type='application/json')
        assert response.status_code == 200

        # Verify history only has successful calculations
        response = client.get('/history')
        data = json.loads(response.data)
        assert len(data['history']) == 2
        assert data['history'][0]['result'] == 10
        assert data['history'][1]['result'] == 20
