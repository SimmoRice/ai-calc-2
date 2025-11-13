"""
Comprehensive Test Suite for Scientific Calculator Functions
Tests cover:
- Trigonometric functions (sin, cos, tan, asin, acos, atan)
- Logarithmic functions (log, ln)
- Exponential and power functions (exp, sqrt, square, reciprocal, power)
- Edge cases and domain errors
- Security validations for scientific functions
"""
import pytest
import json
import math
from app import app, limiter


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


# ============================================================================
# TRIGONOMETRIC FUNCTIONS TESTS
# ============================================================================

class TestTrigonometricFunctions:
    """Test trigonometric functions (sin, cos, tan, asin, acos, atan)"""

    def test_sin_zero(self, client):
        """Test sin(0) = 0"""
        response = client.post('/scientific',
                              data=json.dumps({'function': 'sin', 'value': 0}),
                              content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert abs(data['result'] - 0) < 1e-10

    def test_sin_pi_over_2(self, client):
        """Test sin(π/2) = 1"""
        response = client.post('/scientific',
                              data=json.dumps({'function': 'sin', 'value': math.pi / 2}),
                              content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert abs(data['result'] - 1) < 1e-10

    def test_sin_negative(self, client):
        """Test sin with negative value"""
        response = client.post('/scientific',
                              data=json.dumps({'function': 'sin', 'value': -math.pi / 6}),
                              content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert abs(data['result'] - (-0.5)) < 1e-10

    def test_cos_zero(self, client):
        """Test cos(0) = 1"""
        response = client.post('/scientific',
                              data=json.dumps({'function': 'cos', 'value': 0}),
                              content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert abs(data['result'] - 1) < 1e-10

    def test_cos_pi(self, client):
        """Test cos(π) = -1"""
        response = client.post('/scientific',
                              data=json.dumps({'function': 'cos', 'value': math.pi}),
                              content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert abs(data['result'] - (-1)) < 1e-10

    def test_tan_zero(self, client):
        """Test tan(0) = 0"""
        response = client.post('/scientific',
                              data=json.dumps({'function': 'tan', 'value': 0}),
                              content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert abs(data['result'] - 0) < 1e-10

    def test_tan_pi_over_4(self, client):
        """Test tan(π/4) = 1"""
        response = client.post('/scientific',
                              data=json.dumps({'function': 'tan', 'value': math.pi / 4}),
                              content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert abs(data['result'] - 1) < 1e-10

    def test_asin_zero(self, client):
        """Test asin(0) = 0"""
        response = client.post('/scientific',
                              data=json.dumps({'function': 'asin', 'value': 0}),
                              content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert abs(data['result'] - 0) < 1e-10

    def test_asin_one(self, client):
        """Test asin(1) = π/2"""
        response = client.post('/scientific',
                              data=json.dumps({'function': 'asin', 'value': 1}),
                              content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert abs(data['result'] - math.pi / 2) < 1e-10

    def test_asin_domain_error_high(self, client):
        """Test asin with value > 1 returns domain error"""
        response = client.post('/scientific',
                              data=json.dumps({'function': 'asin', 'value': 1.5}),
                              content_type='application/json')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Domain error' in data['error']

    def test_asin_domain_error_low(self, client):
        """Test asin with value < -1 returns domain error"""
        response = client.post('/scientific',
                              data=json.dumps({'function': 'asin', 'value': -1.5}),
                              content_type='application/json')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Domain error' in data['error']

    def test_acos_zero(self, client):
        """Test acos(0) = π/2"""
        response = client.post('/scientific',
                              data=json.dumps({'function': 'acos', 'value': 0}),
                              content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert abs(data['result'] - math.pi / 2) < 1e-10

    def test_acos_one(self, client):
        """Test acos(1) = 0"""
        response = client.post('/scientific',
                              data=json.dumps({'function': 'acos', 'value': 1}),
                              content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert abs(data['result'] - 0) < 1e-10

    def test_acos_domain_error(self, client):
        """Test acos with value > 1 returns domain error"""
        response = client.post('/scientific',
                              data=json.dumps({'function': 'acos', 'value': 2}),
                              content_type='application/json')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Domain error' in data['error']

    def test_atan_zero(self, client):
        """Test atan(0) = 0"""
        response = client.post('/scientific',
                              data=json.dumps({'function': 'atan', 'value': 0}),
                              content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert abs(data['result'] - 0) < 1e-10

    def test_atan_one(self, client):
        """Test atan(1) = π/4"""
        response = client.post('/scientific',
                              data=json.dumps({'function': 'atan', 'value': 1}),
                              content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert abs(data['result'] - math.pi / 4) < 1e-10

    def test_atan_large_value(self, client):
        """Test atan with large value approaches π/2"""
        response = client.post('/scientific',
                              data=json.dumps({'function': 'atan', 'value': 1000}),
                              content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        # atan(∞) → π/2
        assert abs(data['result'] - math.pi / 2) < 0.01


# ============================================================================
# LOGARITHMIC AND EXPONENTIAL FUNCTIONS TESTS
# ============================================================================

class TestLogarithmicExponentialFunctions:
    """Test logarithmic and exponential functions (log, ln, exp)"""

    def test_log_10(self, client):
        """Test log(10) = 1"""
        response = client.post('/scientific',
                              data=json.dumps({'function': 'log', 'value': 10}),
                              content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert abs(data['result'] - 1) < 1e-10

    def test_log_100(self, client):
        """Test log(100) = 2"""
        response = client.post('/scientific',
                              data=json.dumps({'function': 'log', 'value': 100}),
                              content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert abs(data['result'] - 2) < 1e-10

    def test_log_1(self, client):
        """Test log(1) = 0"""
        response = client.post('/scientific',
                              data=json.dumps({'function': 'log', 'value': 1}),
                              content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert abs(data['result'] - 0) < 1e-10

    def test_log_negative_error(self, client):
        """Test log with negative value returns domain error"""
        response = client.post('/scientific',
                              data=json.dumps({'function': 'log', 'value': -5}),
                              content_type='application/json')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Domain error' in data['error']

    def test_log_zero_error(self, client):
        """Test log(0) returns domain error"""
        response = client.post('/scientific',
                              data=json.dumps({'function': 'log', 'value': 0}),
                              content_type='application/json')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Domain error' in data['error']

    def test_ln_e(self, client):
        """Test ln(e) = 1"""
        response = client.post('/scientific',
                              data=json.dumps({'function': 'ln', 'value': math.e}),
                              content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert abs(data['result'] - 1) < 1e-10

    def test_ln_1(self, client):
        """Test ln(1) = 0"""
        response = client.post('/scientific',
                              data=json.dumps({'function': 'ln', 'value': 1}),
                              content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert abs(data['result'] - 0) < 1e-10

    def test_ln_negative_error(self, client):
        """Test ln with negative value returns domain error"""
        response = client.post('/scientific',
                              data=json.dumps({'function': 'ln', 'value': -1}),
                              content_type='application/json')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Domain error' in data['error']

    def test_exp_zero(self, client):
        """Test exp(0) = 1"""
        response = client.post('/scientific',
                              data=json.dumps({'function': 'exp', 'value': 0}),
                              content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert abs(data['result'] - 1) < 1e-10

    def test_exp_one(self, client):
        """Test exp(1) = e"""
        response = client.post('/scientific',
                              data=json.dumps({'function': 'exp', 'value': 1}),
                              content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert abs(data['result'] - math.e) < 1e-10

    def test_exp_negative(self, client):
        """Test exp with negative value"""
        response = client.post('/scientific',
                              data=json.dumps({'function': 'exp', 'value': -1}),
                              content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert abs(data['result'] - (1 / math.e)) < 1e-10

    def test_exp_large_value(self, client):
        """Test exp with moderately large value"""
        response = client.post('/scientific',
                              data=json.dumps({'function': 'exp', 'value': 5}),
                              content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert abs(data['result'] - math.exp(5)) < 1e-8


# ============================================================================
# POWER AND ADVANCED OPERATIONS TESTS
# ============================================================================

class TestPowerAndAdvancedOperations:
    """Test power, square root, square, and reciprocal functions"""

    def test_sqrt_zero(self, client):
        """Test sqrt(0) = 0"""
        response = client.post('/scientific',
                              data=json.dumps({'function': 'sqrt', 'value': 0}),
                              content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert abs(data['result'] - 0) < 1e-10

    def test_sqrt_4(self, client):
        """Test sqrt(4) = 2"""
        response = client.post('/scientific',
                              data=json.dumps({'function': 'sqrt', 'value': 4}),
                              content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert abs(data['result'] - 2) < 1e-10

    def test_sqrt_25(self, client):
        """Test sqrt(25) = 5"""
        response = client.post('/scientific',
                              data=json.dumps({'function': 'sqrt', 'value': 25}),
                              content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert abs(data['result'] - 5) < 1e-10

    def test_sqrt_negative_error(self, client):
        """Test sqrt with negative value returns domain error"""
        response = client.post('/scientific',
                              data=json.dumps({'function': 'sqrt', 'value': -4}),
                              content_type='application/json')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Domain error' in data['error']

    def test_square_zero(self, client):
        """Test square(0) = 0"""
        response = client.post('/scientific',
                              data=json.dumps({'function': 'square', 'value': 0}),
                              content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['result'] == 0

    def test_square_5(self, client):
        """Test square(5) = 25"""
        response = client.post('/scientific',
                              data=json.dumps({'function': 'square', 'value': 5}),
                              content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['result'] == 25

    def test_square_negative(self, client):
        """Test square(-3) = 9"""
        response = client.post('/scientific',
                              data=json.dumps({'function': 'square', 'value': -3}),
                              content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['result'] == 9

    def test_reciprocal_2(self, client):
        """Test reciprocal(2) = 0.5"""
        response = client.post('/scientific',
                              data=json.dumps({'function': 'reciprocal', 'value': 2}),
                              content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert abs(data['result'] - 0.5) < 1e-10

    def test_reciprocal_4(self, client):
        """Test reciprocal(4) = 0.25"""
        response = client.post('/scientific',
                              data=json.dumps({'function': 'reciprocal', 'value': 4}),
                              content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert abs(data['result'] - 0.25) < 1e-10

    def test_reciprocal_negative(self, client):
        """Test reciprocal(-5) = -0.2"""
        response = client.post('/scientific',
                              data=json.dumps({'function': 'reciprocal', 'value': -5}),
                              content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert abs(data['result'] - (-0.2)) < 1e-10

    def test_reciprocal_zero_error(self, client):
        """Test reciprocal(0) returns division by zero error"""
        response = client.post('/scientific',
                              data=json.dumps({'function': 'reciprocal', 'value': 0}),
                              content_type='application/json')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Division by zero' in data['error']

    def test_power_basic(self, client):
        """Test power(2, 3) = 8"""
        response = client.post('/scientific',
                              data=json.dumps({
                                  'function': 'power',
                                  'value': {'base': 2, 'exponent': 3}
                              }),
                              content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert abs(data['result'] - 8) < 1e-10

    def test_power_zero_exponent(self, client):
        """Test power(5, 0) = 1"""
        response = client.post('/scientific',
                              data=json.dumps({
                                  'function': 'power',
                                  'value': {'base': 5, 'exponent': 0}
                              }),
                              content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert abs(data['result'] - 1) < 1e-10

    def test_power_negative_exponent(self, client):
        """Test power(2, -2) = 0.25"""
        response = client.post('/scientific',
                              data=json.dumps({
                                  'function': 'power',
                                  'value': {'base': 2, 'exponent': -2}
                              }),
                              content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert abs(data['result'] - 0.25) < 1e-10

    def test_power_fractional_exponent(self, client):
        """Test power(4, 0.5) = 2 (square root)"""
        response = client.post('/scientific',
                              data=json.dumps({
                                  'function': 'power',
                                  'value': {'base': 4, 'exponent': 0.5}
                              }),
                              content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert abs(data['result'] - 2) < 1e-10

    def test_power_zero_base(self, client):
        """Test power(0, 2) = 0"""
        response = client.post('/scientific',
                              data=json.dumps({
                                  'function': 'power',
                                  'value': {'base': 0, 'exponent': 2}
                              }),
                              content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert abs(data['result'] - 0) < 1e-10

    def test_power_zero_zero_error(self, client):
        """Test power(0, 0) returns undefined error"""
        response = client.post('/scientific',
                              data=json.dumps({
                                  'function': 'power',
                                  'value': {'base': 0, 'exponent': 0}
                              }),
                              content_type='application/json')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Undefined' in data['error'] or '0^0' in data['error']

    def test_power_negative_base_fractional_exponent_error(self, client):
        """Test power(-4, 0.5) returns error (negative base with fractional exponent)"""
        response = client.post('/scientific',
                              data=json.dumps({
                                  'function': 'power',
                                  'value': {'base': -4, 'exponent': 0.5}
                              }),
                              content_type='application/json')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'negative' in data['error'].lower() or 'fractional' in data['error'].lower()

    def test_power_negative_base_integer_exponent(self, client):
        """Test power(-2, 3) = -8 (negative base with integer exponent)"""
        response = client.post('/scientific',
                              data=json.dumps({
                                  'function': 'power',
                                  'value': {'base': -2, 'exponent': 3}
                              }),
                              content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert abs(data['result'] - (-8)) < 1e-10


# ============================================================================
# SECURITY TESTS FOR SCIENTIFIC FUNCTIONS
# ============================================================================

class TestScientificSecurity:
    """Test security validations for scientific functions"""

    def test_invalid_function_name(self, client):
        """Test that invalid function names are rejected"""
        response = client.post('/scientific',
                              data=json.dumps({'function': 'eval', 'value': 5}),
                              content_type='application/json')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Unknown function' in data['error']

    def test_dangerous_function_names(self, client):
        """Test that dangerous function names are rejected"""
        dangerous_funcs = ['exec', '__import__', 'open', 'compile', 'eval']
        for func in dangerous_funcs:
            response = client.post('/scientific',
                                  data=json.dumps({'function': func, 'value': 5}),
                                  content_type='application/json')
            assert response.status_code == 400

    def test_missing_function_parameter(self, client):
        """Test that missing function parameter is handled"""
        response = client.post('/scientific',
                              data=json.dumps({'value': 5}),
                              content_type='application/json')
        assert response.status_code == 400

    def test_missing_value_parameter(self, client):
        """Test that missing value parameter is handled"""
        response = client.post('/scientific',
                              data=json.dumps({'function': 'sin'}),
                              content_type='application/json')
        assert response.status_code == 400

    def test_invalid_json(self, client):
        """Test that invalid JSON is rejected"""
        response = client.post('/scientific',
                              data='invalid json',
                              content_type='application/json')
        assert response.status_code == 400

    def test_invalid_value_type_string(self, client):
        """Test that non-numeric values are rejected"""
        response = client.post('/scientific',
                              data=json.dumps({'function': 'sin', 'value': 'not a number'}),
                              content_type='application/json')
        assert response.status_code == 400

    def test_invalid_value_type_list(self, client):
        """Test that list values are rejected for single-value functions"""
        response = client.post('/scientific',
                              data=json.dumps({'function': 'sin', 'value': [1, 2, 3]}),
                              content_type='application/json')
        assert response.status_code == 400

    def test_infinity_value_rejected(self, client):
        """Test that infinity values are rejected"""
        response = client.post('/scientific',
                              data=json.dumps({'function': 'sin', 'value': float('inf')}),
                              content_type='application/json')
        assert response.status_code == 400

    def test_nan_value_rejected(self, client):
        """Test that NaN values are rejected"""
        response = client.post('/scientific',
                              data=json.dumps({'function': 'sin', 'value': float('nan')}),
                              content_type='application/json')
        assert response.status_code == 400

    def test_extremely_large_value_rejected(self, client):
        """Test that extremely large values are rejected"""
        response = client.post('/scientific',
                              data=json.dumps({'function': 'sin', 'value': 1e101}),
                              content_type='application/json')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'out of range' in data['error'].lower()

    def test_power_extremely_large_base_rejected(self, client):
        """Test that power with extremely large base is rejected"""
        response = client.post('/scientific',
                              data=json.dumps({
                                  'function': 'power',
                                  'value': {'base': 1e101, 'exponent': 2}
                              }),
                              content_type='application/json')
        assert response.status_code == 400

    def test_power_extremely_large_exponent_rejected(self, client):
        """Test that power with extremely large exponent is rejected"""
        response = client.post('/scientific',
                              data=json.dumps({
                                  'function': 'power',
                                  'value': {'base': 2, 'exponent': 10000}
                              }),
                              content_type='application/json')
        assert response.status_code == 400

    def test_power_invalid_parameters_type(self, client):
        """Test that power with invalid parameter types is rejected"""
        response = client.post('/scientific',
                              data=json.dumps({
                                  'function': 'power',
                                  'value': {'base': 'two', 'exponent': 3}
                              }),
                              content_type='application/json')
        assert response.status_code == 400

    def test_power_missing_parameters(self, client):
        """Test that power with missing parameters is rejected"""
        response = client.post('/scientific',
                              data=json.dumps({
                                  'function': 'power',
                                  'value': {'base': 2}
                              }),
                              content_type='application/json')
        assert response.status_code == 400

    def test_function_name_type_validation(self, client):
        """Test that non-string function names are rejected"""
        response = client.post('/scientific',
                              data=json.dumps({'function': 123, 'value': 5}),
                              content_type='application/json')
        assert response.status_code == 400


# ============================================================================
# EDGE CASES AND INTEGRATION TESTS
# ============================================================================

class TestScientificEdgeCases:
    """Test edge cases for scientific functions"""

    def test_very_small_positive_value(self, client):
        """Test functions with very small positive values"""
        response = client.post('/scientific',
                              data=json.dumps({'function': 'sin', 'value': 1e-10}),
                              content_type='application/json')
        assert response.status_code == 200

    def test_chained_operations(self, client):
        """Test that multiple scientific operations work in sequence"""
        # Calculate sin(0.5)
        response1 = client.post('/scientific',
                               data=json.dumps({'function': 'sin', 'value': 0.5}),
                               content_type='application/json')
        assert response1.status_code == 200
        result1 = json.loads(response1.data)['result']

        # Calculate sqrt(result1)
        response2 = client.post('/scientific',
                               data=json.dumps({'function': 'sqrt', 'value': abs(result1)}),
                               content_type='application/json')
        assert response2.status_code == 200

    def test_power_with_large_but_valid_result(self, client):
        """Test power that produces large but valid result"""
        response = client.post('/scientific',
                              data=json.dumps({
                                  'function': 'power',
                                  'value': {'base': 10, 'exponent': 10}
                              }),
                              content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['result'] == 10000000000

    def test_log_of_very_small_number(self, client):
        """Test logarithm of very small positive number"""
        response = client.post('/scientific',
                              data=json.dumps({'function': 'log', 'value': 0.0001}),
                              content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert abs(data['result'] - (-4)) < 1e-10

    def test_exp_ln_inverse(self, client):
        """Test that exp(ln(x)) = x"""
        test_value = 5
        # Calculate ln(5)
        response1 = client.post('/scientific',
                               data=json.dumps({'function': 'ln', 'value': test_value}),
                               content_type='application/json')
        ln_result = json.loads(response1.data)['result']

        # Calculate exp(ln(5))
        response2 = client.post('/scientific',
                               data=json.dumps({'function': 'exp', 'value': ln_result}),
                               content_type='application/json')
        exp_result = json.loads(response2.data)['result']

        assert abs(exp_result - test_value) < 1e-10

    def test_sqrt_square_inverse(self, client):
        """Test that sqrt(x²) = |x|"""
        test_value = 7
        # Calculate square(7)
        response1 = client.post('/scientific',
                               data=json.dumps({'function': 'square', 'value': test_value}),
                               content_type='application/json')
        square_result = json.loads(response1.data)['result']

        # Calculate sqrt(49)
        response2 = client.post('/scientific',
                               data=json.dumps({'function': 'sqrt', 'value': square_result}),
                               content_type='application/json')
        sqrt_result = json.loads(response2.data)['result']

        assert abs(sqrt_result - test_value) < 1e-10

    def test_decimal_values(self, client):
        """Test scientific functions with decimal values"""
        response = client.post('/scientific',
                              data=json.dumps({'function': 'square', 'value': 3.5}),
                              content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert abs(data['result'] - 12.25) < 1e-10

    def test_negative_values_where_valid(self, client):
        """Test negative values for functions that support them"""
        # sin accepts negative values
        response = client.post('/scientific',
                              data=json.dumps({'function': 'sin', 'value': -1}),
                              content_type='application/json')
        assert response.status_code == 200

        # square accepts negative values
        response = client.post('/scientific',
                              data=json.dumps({'function': 'square', 'value': -5}),
                              content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['result'] == 25


# ============================================================================
# INTEGRATION TESTS WITH BASIC CALCULATOR
# ============================================================================

class TestScientificIntegration:
    """Test integration of scientific functions with basic calculator"""

    def test_scientific_and_basic_operations(self, client):
        """Test using scientific functions alongside basic calculations"""
        # Basic calculation
        response1 = client.post('/calculate',
                               data=json.dumps({'expression': '5+5'}),
                               content_type='application/json')
        assert response1.status_code == 200

        # Scientific calculation
        response2 = client.post('/scientific',
                               data=json.dumps({'function': 'sqrt', 'value': 16}),
                               content_type='application/json')
        assert response2.status_code == 200

        # Another basic calculation
        response3 = client.post('/calculate',
                               data=json.dumps({'expression': '10*2'}),
                               content_type='application/json')
        assert response3.status_code == 200

    def test_all_scientific_functions_exist(self, client):
        """Test that all required scientific functions are implemented"""
        required_functions = [
            'sin', 'cos', 'tan', 'asin', 'acos', 'atan',
            'log', 'ln', 'exp', 'sqrt', 'square', 'reciprocal', 'power'
        ]

        for func in required_functions:
            if func == 'power':
                value = {'base': 2, 'exponent': 2}
            else:
                value = 1

            response = client.post('/scientific',
                                  data=json.dumps({'function': func, 'value': value}),
                                  content_type='application/json')
            # Should either succeed or fail with domain error, not "Unknown function"
            if response.status_code == 400:
                data = json.loads(response.data)
                assert 'Unknown function' not in data['error'], f"Function {func} not implemented"
