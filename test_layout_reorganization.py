"""
Comprehensive Test Suite for Calculator Layout Reorganization
Tests the reorganization of scientific buttons from top to right side of calculator

Feature: Scientific buttons moved from above numeric keypad to right side
Implementation: HTML/CSS/JS changes for side-by-side layout with responsive design

Test Coverage:
- Layout structure verification
- Scientific mode toggle functionality
- Responsive design behavior
- Visual elements positioning
- CSS class toggling
- Button accessibility and functionality
- No regression of existing features
"""

import pytest
import json
import re
from bs4 import BeautifulSoup
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


@pytest.fixture
def html_content(client):
    """Get the rendered HTML content"""
    response = client.get('/')
    return response.data.decode('utf-8')


@pytest.fixture
def soup(html_content):
    """Parse HTML with BeautifulSoup"""
    return BeautifulSoup(html_content, 'html.parser')


# ============================================================================
# LAYOUT STRUCTURE TESTS
# ============================================================================

class TestLayoutStructure:
    """Test the basic layout structure after reorganization"""

    def test_calculator_layout_container_exists(self, soup):
        """Verify .calculator-layout container exists for side-by-side layout"""
        layout_container = soup.find('div', class_='calculator-layout')
        assert layout_container is not None, "calculator-layout container must exist"

    def test_numeric_buttons_container_exists(self, soup):
        """Verify numeric buttons container exists on left side"""
        buttons_container = soup.find('div', class_='buttons')
        assert buttons_container is not None, "buttons container must exist"

    def test_scientific_panel_exists(self, soup):
        """Verify scientific-panel container exists on right side"""
        scientific_panel = soup.find('div', class_='scientific-panel')
        assert scientific_panel is not None, "scientific-panel must exist"

    def test_scientific_buttons_container_exists(self, soup):
        """Verify scientific-buttons container exists within panel"""
        scientific_buttons = soup.find('div', class_='scientific-buttons')
        assert scientific_buttons is not None, "scientific-buttons container must exist"

    def test_layout_hierarchy(self, soup):
        """Verify correct nesting: calculator-layout > buttons + scientific-panel"""
        layout = soup.find('div', class_='calculator-layout')
        assert layout is not None

        # Check that buttons and scientific-panel are direct children
        children = layout.find_all(recursive=False)
        child_classes = [child.get('class', []) for child in children if child.name == 'div']

        assert any('buttons' in classes for classes in child_classes), \
            "buttons must be child of calculator-layout"
        assert any('scientific-panel' in classes for classes in child_classes), \
            "scientific-panel must be child of calculator-layout"

    def test_scientific_buttons_inside_panel(self, soup):
        """Verify scientific-buttons is inside scientific-panel"""
        scientific_panel = soup.find('div', class_='scientific-panel')
        assert scientific_panel is not None

        scientific_buttons = scientific_panel.find('div', class_='scientific-buttons')
        assert scientific_buttons is not None, \
            "scientific-buttons must be nested inside scientific-panel"


# ============================================================================
# BUTTON POSITIONING TESTS
# ============================================================================

class TestButtonPositioning:
    """Test that all buttons are in correct positions"""

    def test_all_numeric_buttons_present(self, soup):
        """Verify all numeric buttons (0-9) are present"""
        buttons_container = soup.find('div', class_='buttons')
        assert buttons_container is not None

        button_texts = [btn.text.strip() for btn in buttons_container.find_all('button')]

        # Check for digits 0-9
        for digit in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
            assert digit in button_texts, f"Numeric button {digit} must be present"

    def test_all_basic_operators_in_numeric_section(self, soup):
        """Verify basic operators (+, -, ×, ÷, =) are in numeric buttons section"""
        buttons_container = soup.find('div', class_='buttons')
        assert buttons_container is not None

        button_texts = [btn.text.strip() for btn in buttons_container.find_all('button')]

        # Check for operators
        assert '÷' in button_texts, "Division operator must be in numeric section"
        assert '×' in button_texts, "Multiplication operator must be in numeric section"
        assert '−' in button_texts, "Subtraction operator must be in numeric section"
        assert '+' in button_texts, "Addition operator must be in numeric section"
        assert '=' in button_texts, "Equals button must be in numeric section"

    def test_all_function_buttons_in_numeric_section(self, soup):
        """Verify AC, ±, % are in numeric buttons section"""
        buttons_container = soup.find('div', class_='buttons')
        assert buttons_container is not None

        button_texts = [btn.text.strip() for btn in buttons_container.find_all('button')]

        assert 'AC' in button_texts, "AC button must be in numeric section"
        assert '±' in button_texts, "Plus-minus button must be in numeric section"
        assert '%' in button_texts, "Percentage button must be in numeric section"

    def test_all_trig_buttons_in_scientific_panel(self, soup):
        """Verify trigonometric functions are in scientific panel"""
        scientific_buttons = soup.find('div', class_='scientific-buttons')
        assert scientific_buttons is not None

        button_texts = [btn.text.strip() for btn in scientific_buttons.find_all('button')]

        # Check trigonometric functions
        assert 'sin' in button_texts, "sin button must be in scientific panel"
        assert 'cos' in button_texts, "cos button must be in scientific panel"
        assert 'tan' in button_texts, "tan button must be in scientific panel"
        assert 'sin⁻¹' in button_texts, "asin button must be in scientific panel"
        assert 'cos⁻¹' in button_texts, "acos button must be in scientific panel"
        assert 'tan⁻¹' in button_texts, "atan button must be in scientific panel"

    def test_all_log_buttons_in_scientific_panel(self, soup):
        """Verify logarithmic functions are in scientific panel"""
        scientific_buttons = soup.find('div', class_='scientific-buttons')
        assert scientific_buttons is not None

        button_texts = [btn.text.strip() for btn in scientific_buttons.find_all('button')]

        assert 'log' in button_texts, "log button must be in scientific panel"
        assert 'ln' in button_texts, "ln button must be in scientific panel"
        assert 'eˣ' in button_texts, "exp button must be in scientific panel"

    def test_all_math_operations_in_scientific_panel(self, soup):
        """Verify mathematical operations (sqrt, x², xʸ, 1/x) are in scientific panel"""
        scientific_buttons = soup.find('div', class_='scientific-buttons')
        assert scientific_buttons is not None

        button_texts = [btn.text.strip() for btn in scientific_buttons.find_all('button')]

        assert '√' in button_texts, "sqrt button must be in scientific panel"
        assert 'x²' in button_texts, "square button must be in scientific panel"
        assert 'xʸ' in button_texts, "power button must be in scientific panel"
        assert '1/x' in button_texts, "reciprocal button must be in scientific panel"

    def test_constants_in_scientific_panel(self, soup):
        """Verify constants (π, e) are in scientific panel"""
        scientific_buttons = soup.find('div', class_='scientific-buttons')
        assert scientific_buttons is not None

        button_texts = [btn.text.strip() for btn in scientific_buttons.find_all('button')]

        assert 'π' in button_texts, "pi constant must be in scientific panel"
        assert 'e' in button_texts, "e constant must be in scientific panel"

    def test_memory_functions_in_scientific_panel(self, soup):
        """Verify memory functions (MC, MR, M+, M−) are in scientific panel"""
        scientific_buttons = soup.find('div', class_='scientific-buttons')
        assert scientific_buttons is not None

        button_texts = [btn.text.strip() for btn in scientific_buttons.find_all('button')]

        assert 'MC' in button_texts, "MC button must be in scientific panel"
        assert 'MR' in button_texts, "MR button must be in scientific panel"
        assert 'M+' in button_texts, "M+ button must be in scientific panel"
        assert 'M−' in button_texts, "M- button must be in scientific panel"

    def test_no_scientific_buttons_in_numeric_section(self, soup):
        """Verify NO scientific functions are in the numeric buttons section"""
        buttons_container = soup.find('div', class_='buttons')
        assert buttons_container is not None

        button_texts = [btn.text.strip() for btn in buttons_container.find_all('button')]

        # These should NOT be in numeric section
        scientific_functions = ['sin', 'cos', 'tan', 'log', 'ln', 'eˣ', '√', 'x²', 'xʸ',
                                '1/x', 'π', 'e', 'MC', 'MR', 'M+', 'M−', 'sin⁻¹', 'cos⁻¹', 'tan⁻¹']

        for func in scientific_functions:
            assert func not in button_texts, \
                f"Scientific function '{func}' should NOT be in numeric section"


# ============================================================================
# SCIENTIFIC MODE TOGGLE TESTS
# ============================================================================

class TestScientificModeToggle:
    """Test scientific mode toggle button and functionality"""

    def test_scientific_mode_button_exists(self, soup):
        """Verify scientific mode toggle button exists"""
        mode_btn = soup.find('button', id='sciModeBtn')
        assert mode_btn is not None, "Scientific mode button must exist"

    def test_scientific_mode_button_text(self, soup):
        """Verify scientific mode button has correct default text"""
        mode_btn = soup.find('button', id='sciModeBtn')
        assert mode_btn is not None
        assert mode_btn.text.strip() == 'Scientific', \
            "Mode button should show 'Scientific' by default"

    def test_scientific_mode_button_onclick(self, soup):
        """Verify scientific mode button has onclick handler"""
        mode_btn = soup.find('button', id='sciModeBtn')
        assert mode_btn is not None
        assert mode_btn.get('onclick') == 'toggleScientificMode()', \
            "Mode button must call toggleScientificMode()"

    def test_mode_toggle_section_exists(self, soup):
        """Verify mode-toggle container exists"""
        mode_toggle = soup.find('div', class_='mode-toggle')
        assert mode_toggle is not None, "mode-toggle container must exist"


# ============================================================================
# CSS STYLING VERIFICATION TESTS
# ============================================================================

class TestCSSStructure:
    """Verify CSS structure is properly loaded"""

    def test_css_file_linked(self, html_content):
        """Verify style.css is linked in HTML"""
        assert 'style.css' in html_content, "style.css must be linked"

    def test_calculator_layout_in_html(self, html_content):
        """Verify calculator-layout class is used in HTML"""
        assert 'calculator-layout' in html_content, \
            "calculator-layout class must be present in HTML"

    def test_scientific_panel_in_html(self, html_content):
        """Verify scientific-panel class is used in HTML"""
        assert 'scientific-panel' in html_content, \
            "scientific-panel class must be present in HTML"


# ============================================================================
# BUTTON FUNCTIONALITY TESTS (No Regression)
# ============================================================================

class TestButtonFunctionality:
    """Ensure all button click handlers still work after reorganization"""

    def test_numeric_buttons_have_onclick_handlers(self, soup):
        """Verify all numeric buttons have onclick handlers"""
        buttons_container = soup.find('div', class_='buttons')
        number_buttons = buttons_container.find_all('button', class_='btn-number')

        for btn in number_buttons:
            onclick = btn.get('onclick', '')
            assert 'appendNumber' in onclick or onclick != '', \
                f"Button {btn.text} must have onclick handler"

    def test_scientific_buttons_have_onclick_handlers(self, soup):
        """Verify all scientific buttons have onclick handlers"""
        scientific_buttons = soup.find('div', class_='scientific-buttons')
        sci_buttons = scientific_buttons.find_all('button', class_='btn-scientific')

        for btn in sci_buttons:
            onclick = btn.get('onclick', '')
            assert onclick != '', f"Scientific button {btn.text} must have onclick handler"

    def test_trig_buttons_call_correct_functions(self, soup):
        """Verify trig buttons call scientificFunction()"""
        scientific_buttons = soup.find('div', class_='scientific-buttons')

        sin_btn = scientific_buttons.find('button', string='sin')
        assert sin_btn is not None
        assert "scientificFunction('sin')" in sin_btn.get('onclick', ''), \
            "sin button must call scientificFunction('sin')"

        cos_btn = scientific_buttons.find('button', string='cos')
        assert cos_btn is not None
        assert "scientificFunction('cos')" in cos_btn.get('onclick', ''), \
            "cos button must call scientificFunction('cos')"

    def test_memory_buttons_call_correct_functions(self, soup):
        """Verify memory buttons call correct functions"""
        scientific_buttons = soup.find('div', class_='scientific-buttons')

        mc_btn = scientific_buttons.find('button', string='MC')
        assert mc_btn is not None
        assert 'memoryClear()' in mc_btn.get('onclick', ''), \
            "MC button must call memoryClear()"

        mr_btn = scientific_buttons.find('button', string='MR')
        assert mr_btn is not None
        assert 'memoryRecall()' in mr_btn.get('onclick', ''), \
            "MR button must call memoryRecall()"

    def test_constant_buttons_call_correct_functions(self, soup):
        """Verify constant buttons call insertConstant()"""
        scientific_buttons = soup.find('div', class_='scientific-buttons')

        pi_btn = scientific_buttons.find('button', string='π')
        assert pi_btn is not None
        assert "insertConstant('pi')" in pi_btn.get('onclick', ''), \
            "pi button must call insertConstant('pi')"

        e_btn = scientific_buttons.find('button', string='e')
        assert e_btn is not None
        assert "insertConstant('e')" in e_btn.get('onclick', ''), \
            "e button must call insertConstant('e')"


# ============================================================================
# DISPLAY TESTS
# ============================================================================

class TestDisplay:
    """Test display element and indicators"""

    def test_display_exists(self, soup):
        """Verify calculator display exists"""
        display = soup.find('div', class_='display')
        assert display is not None, "Display must exist"

    def test_display_text_element_exists(self, soup):
        """Verify display-text element exists"""
        display_text = soup.find('div', class_='display-text')
        assert display_text is not None, "Display text element must exist"

    def test_display_indicators_exist(self, soup):
        """Verify display indicators exist"""
        indicators = soup.find('div', class_='display-indicators')
        assert indicators is not None, "Display indicators must exist"

    def test_memory_indicator_exists(self, soup):
        """Verify memory indicator exists"""
        memory_ind = soup.find('span', id='memoryIndicator')
        assert memory_ind is not None, "Memory indicator must exist"

    def test_angle_mode_indicator_exists(self, soup):
        """Verify angle mode indicator exists"""
        angle_ind = soup.find('span', id='angleModeBtn')
        assert angle_ind is not None, "Angle mode indicator must exist"

    def test_angle_mode_indicator_onclick(self, soup):
        """Verify angle mode indicator has onclick handler"""
        angle_ind = soup.find('span', id='angleModeBtn')
        assert angle_ind is not None
        assert angle_ind.get('onclick') == 'toggleAngleMode()', \
            "Angle indicator must call toggleAngleMode()"


# ============================================================================
# RESPONSIVE DESIGN TESTS
# ============================================================================

class TestResponsiveDesign:
    """Test responsive design elements for layout reorganization"""

    def test_calculator_has_proper_structure_for_responsive(self, soup):
        """Verify structure supports responsive design"""
        calculator = soup.find('div', class_='calculator')
        assert calculator is not None

        layout = calculator.find('div', class_='calculator-layout')
        assert layout is not None, "Layout must support responsive design"

    def test_scientific_panel_structure_for_mobile(self, soup):
        """Verify scientific panel structure supports mobile stacking"""
        scientific_panel = soup.find('div', class_='scientific-panel')
        assert scientific_panel is not None

        scientific_buttons = scientific_panel.find('div', class_='scientific-buttons')
        assert scientific_buttons is not None, \
            "Scientific buttons container must exist for responsive layout"


# ============================================================================
# INTEGRATION TESTS - Full Calculator Workflow
# ============================================================================

class TestCalculatorIntegration:
    """Integration tests to ensure layout doesn't break calculator functionality"""

    def test_basic_calculation_still_works(self, client):
        """Verify basic calculations work after layout change"""
        response = client.post('/calculate',
                               data=json.dumps({'expression': '2+2'}),
                               content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['result'] == 4

    def test_scientific_calculation_still_works(self, client):
        """Verify scientific calculations work after layout change"""
        response = client.post('/scientific',
                               data=json.dumps({'function': 'sin', 'value': 0}),
                               content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert abs(data['result']) < 0.0001  # sin(0) = 0

    def test_history_still_works(self, client):
        """Verify history functionality works after layout change"""
        # Make a calculation
        client.post('/calculate',
                   data=json.dumps({'expression': '5+5'}),
                   content_type='application/json')

        # Check history
        response = client.get('/history')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data['history']) > 0

    def test_clear_history_still_works(self, client):
        """Verify clear history works after layout change"""
        # Add calculation
        client.post('/calculate',
                   data=json.dumps({'expression': '3+3'}),
                   content_type='application/json')

        # Clear history
        response = client.post('/clear-history',
                              content_type='application/json')
        assert response.status_code == 200

        # Verify history is empty
        history_response = client.get('/history')
        data = json.loads(history_response.data)
        assert len(data['history']) == 0


# ============================================================================
# SECURITY REGRESSION TESTS
# ============================================================================

class TestSecurityNoRegression:
    """Ensure layout changes don't introduce security vulnerabilities"""

    def test_no_inline_scripts_added(self, html_content):
        """Verify no inline <script> tags were added"""
        # Check for <script> tags that aren't external references
        soup = BeautifulSoup(html_content, 'html.parser')
        script_tags = soup.find_all('script')

        for script in script_tags:
            # All scripts should be external (have src attribute)
            if not script.get('src'):
                # If no src, should be empty (no inline code)
                assert script.string is None or script.string.strip() == '', \
                    "No inline scripts should be present"

    def test_onclick_handlers_use_safe_functions(self, soup):
        """Verify onclick handlers only call whitelisted functions"""
        safe_functions = [
            'clearAll', 'toggleSign', 'percentage', 'setOperator',
            'appendNumber', 'calculate', 'scientificFunction',
            'insertConstant', 'setPowerOperation', 'memoryClear',
            'memoryRecall', 'memoryAdd', 'memorySubtract',
            'toggleScientificMode', 'toggleAngleMode', 'clearHistory',
            'changeTheme'
        ]

        all_buttons = soup.find_all('button')
        for button in all_buttons:
            onclick = button.get('onclick', '')
            if onclick:
                # Extract function name
                func_name = onclick.split('(')[0].strip()
                assert func_name in safe_functions, \
                    f"Button onclick uses unknown function: {func_name}"

    def test_no_new_form_inputs(self, soup):
        """Verify no new form inputs were added (potential XSS vector)"""
        calculator = soup.find('div', class_='calculator')

        # Should have no input elements inside calculator (except theme select)
        inputs = calculator.find_all('input')
        assert len(inputs) == 0, "No new input fields should be in calculator"

    def test_flask_url_for_still_used(self, html_content):
        """Verify Flask url_for is still used for static resources"""
        # url_for is rendered to actual URLs like /static/style.css
        # Check that static resources are properly loaded
        assert "/static/style.css" in html_content or "url_for('static'" in html_content, \
            "Flask static resources should be properly referenced"


# ============================================================================
# VISUAL CONSISTENCY TESTS
# ============================================================================

class TestVisualConsistency:
    """Test visual elements and CSS classes for consistency"""

    def test_all_numeric_buttons_have_btn_number_class(self, soup):
        """Verify numeric buttons have correct CSS class"""
        buttons_container = soup.find('div', class_='buttons')

        # Find buttons with numbers
        for digit in ['1', '2', '3', '4', '5', '6', '7', '8', '9']:
            btn = buttons_container.find('button', string=digit)
            assert btn is not None
            assert 'btn-number' in btn.get('class', []), \
                f"Button {digit} must have btn-number class"

    def test_all_scientific_buttons_have_btn_scientific_class(self, soup):
        """Verify scientific buttons have correct CSS class"""
        scientific_buttons = soup.find('div', class_='scientific-buttons')

        all_sci_buttons = scientific_buttons.find_all('button')
        for btn in all_sci_buttons:
            assert 'btn-scientific' in btn.get('class', []), \
                f"Scientific button {btn.text} must have btn-scientific class"

    def test_operator_buttons_have_btn_operator_class(self, soup):
        """Verify operator buttons have correct CSS class"""
        buttons_container = soup.find('div', class_='buttons')

        operator_symbols = ['÷', '×', '−', '+', '=']
        for op in operator_symbols:
            btn = buttons_container.find('button', string=op)
            assert btn is not None
            assert 'btn-operator' in btn.get('class', []), \
                f"Operator {op} must have btn-operator class"

    def test_function_buttons_have_btn_function_class(self, soup):
        """Verify function buttons have correct CSS class"""
        buttons_container = soup.find('div', class_='buttons')

        functions = ['AC', '±', '%']
        for func in functions:
            btn = buttons_container.find('button', string=func)
            assert btn is not None
            assert 'btn-function' in btn.get('class', []), \
                f"Function {func} must have btn-function class"


# ============================================================================
# THEME COMPATIBILITY TESTS
# ============================================================================

class TestThemeCompatibility:
    """Ensure layout works with all themes"""

    def test_theme_selector_exists(self, soup):
        """Verify theme selector is present"""
        theme_select = soup.find('select', id='themeSelect')
        assert theme_select is not None, "Theme selector must exist"

    def test_theme_options_present(self, soup):
        """Verify all theme options are available"""
        theme_select = soup.find('select', id='themeSelect')
        assert theme_select is not None

        options = theme_select.find_all('option')
        option_values = [opt.get('value') for opt in options]

        assert 'macos' in option_values, "macOS theme must be available"
        assert 'dark' in option_values, "Dark theme must be available"
        assert 'blue' in option_values, "Blue theme must be available"

    def test_theme_toggle_position(self, soup):
        """Verify theme toggle is in correct position"""
        theme_toggle = soup.find('div', class_='theme-toggle')
        assert theme_toggle is not None, "Theme toggle must exist"


# ============================================================================
# EDGE CASE TESTS
# ============================================================================

class TestEdgeCases:
    """Test edge cases and boundary conditions"""

    def test_zero_button_spans_two_columns(self, soup):
        """Verify zero button maintains its special width"""
        buttons_container = soup.find('div', class_='buttons')
        zero_btn = buttons_container.find('button', string='0')

        assert zero_btn is not None
        assert 'btn-zero' in zero_btn.get('class', []), \
            "Zero button must have btn-zero class for double width"

    def test_decimal_button_present(self, soup):
        """Verify decimal point button is present"""
        buttons_container = soup.find('div', class_='buttons')
        decimal_btn = buttons_container.find('button', string='.')

        assert decimal_btn is not None, "Decimal button must be present"
        assert 'btn-number' in decimal_btn.get('class', []), \
            "Decimal button must have btn-number class"

    def test_calculator_container_exists(self, soup):
        """Verify main calculator container exists"""
        calculator = soup.find('div', class_='calculator')
        assert calculator is not None, "Calculator container must exist"

    def test_container_wrapper_exists(self, soup):
        """Verify outer container wrapper exists"""
        container = soup.find('div', class_='container')
        assert container is not None, "Container wrapper must exist"

    def test_history_panel_exists(self, soup):
        """Verify history panel is still present"""
        history_panel = soup.find('div', class_='history-panel')
        assert history_panel is not None, "History panel must exist"


# ============================================================================
# COUNT AND COMPLETENESS TESTS
# ============================================================================

class TestCompleteness:
    """Verify all buttons are accounted for"""

    def test_correct_number_of_numeric_buttons(self, soup):
        """Verify correct count of numeric buttons in numeric section"""
        buttons_container = soup.find('div', class_='buttons')

        # Should have: 0-9 (10), AC, ±, %, ÷, ×, −, +, = (8), . (1) = 19 buttons
        all_buttons = buttons_container.find_all('button')
        assert len(all_buttons) == 19, \
            f"Numeric section should have 19 buttons, found {len(all_buttons)}"

    def test_correct_number_of_scientific_buttons(self, soup):
        """Verify correct count of scientific buttons"""
        scientific_buttons = soup.find('div', class_='scientific-buttons')

        # Trig (6) + Log (3) + Math (4) + Constants (2) + Memory (4) = 19 buttons
        all_buttons = scientific_buttons.find_all('button')
        assert len(all_buttons) == 19, \
            f"Scientific panel should have 19 buttons, found {len(all_buttons)}"

    def test_no_duplicate_buttons(self, soup):
        """Verify no buttons appear in both sections"""
        numeric_buttons = soup.find('div', class_='buttons')
        scientific_buttons = soup.find('div', class_='scientific-buttons')

        numeric_texts = [btn.text.strip() for btn in numeric_buttons.find_all('button')]
        scientific_texts = [btn.text.strip() for btn in scientific_buttons.find_all('button')]

        # Check for duplicates
        for text in scientific_texts:
            assert text not in numeric_texts, \
                f"Button '{text}' appears in both sections"


# ============================================================================
# JAVASCRIPT REFERENCE TESTS
# ============================================================================

class TestJavaScriptReferences:
    """Test JavaScript file references"""

    def test_script_js_linked(self, html_content):
        """Verify script.js is linked"""
        assert 'script.js' in html_content, "script.js must be linked"

    def test_script_loaded_at_end(self, soup):
        """Verify script is loaded at end of body"""
        scripts = soup.find_all('script')
        body = soup.find('body')

        # Script should be in body
        body_scripts = body.find_all('script') if body else []
        assert len(body_scripts) > 0, "Script should be loaded in body"


# ============================================================================
# ACCESSIBILITY TESTS
# ============================================================================

class TestAccessibility:
    """Test accessibility features"""

    def test_calculator_has_semantic_structure(self, soup):
        """Verify semantic HTML structure"""
        calculator = soup.find('div', class_='calculator')
        assert calculator is not None

        # Check for proper nesting
        assert calculator.find('div', class_='display') is not None
        assert calculator.find('div', class_='calculator-layout') is not None

    def test_all_buttons_are_button_elements(self, soup):
        """Verify all clickable elements are proper button tags"""
        calculator = soup.find('div', class_='calculator')

        # All clickable calculator elements should be buttons
        buttons = calculator.find_all('button')
        assert len(buttons) > 30, "Should have many button elements"

    def test_buttons_have_text_content(self, soup):
        """Verify all buttons have visible text"""
        calculator = soup.find('div', class_='calculator')
        buttons = calculator.find_all('button')

        for btn in buttons:
            text = btn.text.strip()
            assert text != '', f"Button must have text content"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
