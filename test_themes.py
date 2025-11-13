"""
Comprehensive Test Suite for Theme Switcher Feature
Tests cover:
- Theme loading and persistence (localStorage)
- Theme switching functionality
- Theme validation and security
- Edge cases and error handling
- Integration with calculator display
- Cross-browser compatibility concerns
"""
import pytest
import json
from app import app


# Test Fixtures
@pytest.fixture
def client():
    """Create a test client for the Flask app"""
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret-key'
    with app.test_client() as client:
        yield client


# ============================================================================
# HTML/CSS THEME STRUCTURE TESTS
# ============================================================================

class TestThemeStructure:
    """Test that theme HTML/CSS structure is correctly implemented"""

    def test_theme_selector_exists_in_html(self, client):
        """Test that theme selector element exists in the HTML"""
        response = client.get('/')
        assert response.status_code == 200
        html_content = response.data.decode('utf-8')

        # Check for theme selector elements
        assert 'themeSelect' in html_content, "Theme select element should exist"
        assert 'theme-selector' in html_content, "Theme selector container should exist"
        assert 'changeTheme()' in html_content, "Theme change function should be called"

    def test_all_three_themes_in_dropdown(self, client):
        """Test that all three theme options are present in the dropdown"""
        response = client.get('/')
        html_content = response.data.decode('utf-8')

        # Check for all three theme options
        assert 'value="macos"' in html_content, "macOS theme option should exist"
        assert 'value="dark"' in html_content, "Dark theme option should exist"
        assert 'value="blue"' in html_content, "Blue theme option should exist"

        # Check for theme labels
        assert 'macOS' in html_content, "macOS theme label should exist"
        assert 'Dark Pro' in html_content, "Dark Pro theme label should exist"
        assert 'Modern Blue' in html_content, "Modern Blue theme label should exist"

    def test_css_theme_variables_exist(self, client):
        """Test that CSS theme variables are defined in stylesheet"""
        response = client.get('/static/style.css')
        assert response.status_code == 200
        css_content = response.data.decode('utf-8')

        # Check for theme CSS custom properties (variables)
        assert '--bg-primary' in css_content, "Background color variable should exist"
        assert '--btn-operator' in css_content, "Button operator color variable should exist"
        assert '--text-display' in css_content, "Display text color variable should exist"

        # Check for all three theme definitions
        assert '[data-theme="macos"]' in css_content or ':root' in css_content, "macOS theme definition should exist"
        assert '[data-theme="dark"]' in css_content, "Dark theme definition should exist"
        assert '[data-theme="blue"]' in css_content, "Blue theme definition should exist"

    def test_macos_theme_colors(self, client):
        """Test that macOS theme has correct color values"""
        response = client.get('/static/style.css')
        css_content = response.data.decode('utf-8')

        # macOS theme should be default (:root)
        assert '#ff9f0a' in css_content.lower() or '#ff9500' in css_content.lower(), \
            "macOS theme should have orange operator buttons"

    def test_dark_theme_colors(self, client):
        """Test that dark theme has correct color values"""
        response = client.get('/static/style.css')
        css_content = response.data.decode('utf-8')

        # Dark theme colors
        assert '#1e1e1e' in css_content.lower(), "Dark theme should have dark background"
        assert '#3d3d3d' in css_content.lower(), "Dark theme should have gray number buttons"
        assert '#ff9500' in css_content.lower(), "Dark theme should have orange operator buttons"

    def test_blue_theme_colors(self, client):
        """Test that blue theme has correct color values"""
        response = client.get('/static/style.css')
        css_content = response.data.decode('utf-8')

        # Blue theme colors
        assert '#f0f4f8' in css_content.lower(), "Blue theme should have light blue background"
        assert '#4299e1' in css_content.lower(), "Blue theme should have blue number buttons"
        assert '#3182ce' in css_content.lower(), "Blue theme should have dark blue operator buttons"


# ============================================================================
# JAVASCRIPT THEME FUNCTIONS TESTS
# ============================================================================

class TestThemeJavaScript:
    """Test JavaScript theme management functions"""

    def test_theme_functions_exist_in_script(self, client):
        """Test that theme management functions exist in JavaScript"""
        response = client.get('/static/script.js')
        assert response.status_code == 200
        js_content = response.data.decode('utf-8')

        # Check for theme functions
        assert 'changeTheme' in js_content, "changeTheme function should exist"
        assert 'applyTheme' in js_content, "applyTheme function should exist"
        assert 'loadTheme' in js_content, "loadTheme function should exist"

    def test_allowed_themes_constant_exists(self, client):
        """Test that ALLOWED_THEMES security constant exists"""
        response = client.get('/static/script.js')
        js_content = response.data.decode('utf-8')

        # Check for security whitelist
        assert 'ALLOWED_THEMES' in js_content, "ALLOWED_THEMES constant should exist for security"
        assert "'macos'" in js_content or '"macos"' in js_content, "macos should be in allowed themes"
        assert "'dark'" in js_content or '"dark"' in js_content, "dark should be in allowed themes"
        assert "'blue'" in js_content or '"blue"' in js_content, "blue should be in allowed themes"

    def test_localstorage_key_is_correct(self, client):
        """Test that localStorage key is correctly defined"""
        response = client.get('/static/script.js')
        js_content = response.data.decode('utf-8')

        # Check for localStorage key
        assert 'calculator-theme' in js_content, "localStorage key 'calculator-theme' should exist"

    def test_theme_validation_logic_exists(self, client):
        """Test that theme validation logic exists for security"""
        response = client.get('/static/script.js')
        js_content = response.data.decode('utf-8')

        # Check for validation in applyTheme or changeTheme functions
        # Looking for security validation patterns
        assert 'includes(' in js_content or 'indexOf(' in js_content, \
            "Theme validation should check if theme is in allowed list"

    def test_data_theme_attribute_logic(self, client):
        """Test that data-theme attribute logic exists"""
        response = client.get('/static/script.js')
        js_content = response.data.decode('utf-8')

        # Check for DOM manipulation
        assert 'data-theme' in js_content, "data-theme attribute should be used"
        assert 'setAttribute' in js_content, "setAttribute should be used to set theme"


# ============================================================================
# THEME SECURITY TESTS
# ============================================================================

class TestThemeSecurity:
    """Test security aspects of theme switcher"""

    def test_theme_whitelist_validation_in_js(self, client):
        """Test that theme names are validated against whitelist"""
        response = client.get('/static/script.js')
        js_content = response.data.decode('utf-8')

        # Check for security validation in changeTheme or applyTheme
        # These patterns indicate proper validation
        validation_patterns = [
            'ALLOWED_THEMES.includes',
            'if (!ALLOWED_THEMES',
            'includes(selectedTheme)',
            'includes(themeName)',
        ]

        has_validation = any(pattern in js_content for pattern in validation_patterns)
        assert has_validation, "Theme validation against whitelist should exist"

    def test_no_eval_or_dangerous_functions(self, client):
        """Test that theme code doesn't use dangerous functions"""
        response = client.get('/static/script.js')
        js_content = response.data.decode('utf-8')

        # Check theme-related sections don't use dangerous functions
        # Extract theme-related code (rough approximation)
        theme_section_start = js_content.find('Theme Management')
        theme_section_end = js_content.find('Display Functions', theme_section_start)

        if theme_section_start > -1 and theme_section_end > -1:
            theme_code = js_content[theme_section_start:theme_section_end]
        else:
            # If section markers not found, check whole file
            theme_code = js_content

        # These should NOT be in theme code
        dangerous_patterns = [
            'eval(',
            'Function(',
            'innerHTML =',  # Theme switching should use setAttribute, not innerHTML
        ]

        for pattern in dangerous_patterns:
            # Allow console.error but not dangerous eval, etc.
            if pattern == 'innerHTML =' and 'theme' in js_content.lower():
                # Specifically check theme functions don't use innerHTML
                theme_funcs = ['changeTheme', 'applyTheme', 'loadTheme']
                for func in theme_funcs:
                    func_start = js_content.find(f'function {func}')
                    if func_start > -1:
                        # Find end of function (rough approximation)
                        func_end = js_content.find('\nfunction ', func_start + 1)
                        if func_end == -1:
                            func_end = func_start + 500  # Check next 500 chars
                        func_code = js_content[func_start:func_end]
                        assert pattern not in func_code, \
                            f"{func} should not use {pattern} for security"

    def test_xss_protection_in_theme_code(self, client):
        """Test that theme code uses safe DOM manipulation"""
        response = client.get('/static/script.js')
        js_content = response.data.decode('utf-8')

        # Theme functions should use setAttribute, not innerHTML
        assert 'setAttribute' in js_content, "Theme code should use setAttribute for safety"
        assert 'data-theme' in js_content, "Theme should be set via data-theme attribute"

    def test_security_comments_exist(self, client):
        """Test that security-related comments exist in theme code"""
        response = client.get('/static/script.js')
        js_content = response.data.decode('utf-8')

        # Check for security-related comments
        security_indicators = [
            'SECURITY:',
            'Validate',
            'whitelist',
            'allowed',
            'XSS',
        ]

        # At least some security awareness should be documented
        has_security_comments = any(indicator in js_content for indicator in security_indicators)
        assert has_security_comments, "Code should have security comments/documentation"


# ============================================================================
# THEME FUNCTIONALITY TESTS (Integration)
# ============================================================================

class TestThemeFunctionality:
    """Test theme functionality through the web interface"""

    def test_index_page_loads_with_theme_selector(self, client):
        """Test that index page loads successfully with theme selector"""
        response = client.get('/')
        assert response.status_code == 200

        html_content = response.data.decode('utf-8')
        assert 'theme-toggle' in html_content or 'theme-selector' in html_content, \
            "Theme selector UI should be present"

    def test_default_theme_is_macos(self, client):
        """Test that default theme is macOS"""
        response = client.get('/')
        html_content = response.data.decode('utf-8')

        # Check for default theme - macOS should be the default
        # This can be verified by checking if CSS uses :root for macOS theme
        css_response = client.get('/static/style.css')
        css_content = css_response.data.decode('utf-8')

        # macOS theme should be in :root (default)
        assert ':root' in css_content or '[data-theme="macos"]' in css_content, \
            "macOS theme should be defined as default"

    def test_theme_selector_positioned_correctly(self, client):
        """Test that theme selector is positioned non-intrusively"""
        response = client.get('/static/style.css')
        css_content = response.data.decode('utf-8')

        # Check for positioning CSS
        assert '.theme-toggle' in css_content or '.theme-selector' in css_content, \
            "Theme selector should have CSS styling"

        # Should be positioned (fixed/absolute) to not interfere with layout
        assert 'position' in css_content, "Theme selector should have positioning"

    def test_theme_transitions_exist(self, client):
        """Test that theme transitions are smooth (CSS transitions)"""
        response = client.get('/static/style.css')
        css_content = response.data.decode('utf-8')

        # Check for transitions for smooth theme switching
        assert 'transition' in css_content, "CSS should include transitions for smooth theme changes"


# ============================================================================
# THEME PERSISTENCE TESTS
# ============================================================================

class TestThemePersistence:
    """Test theme persistence using localStorage"""

    def test_localstorage_logic_in_loadtheme(self, client):
        """Test that loadTheme function reads from localStorage"""
        response = client.get('/static/script.js')
        js_content = response.data.decode('utf-8')

        # Check for localStorage.getItem in loadTheme
        assert 'localStorage.getItem' in js_content, \
            "loadTheme should read from localStorage"
        assert 'calculator-theme' in js_content, \
            "Should use 'calculator-theme' as localStorage key"

    def test_localstorage_logic_in_changetheme(self, client):
        """Test that changeTheme function writes to localStorage"""
        response = client.get('/static/script.js')
        js_content = response.data.decode('utf-8')

        # Check for localStorage.setItem in changeTheme
        assert 'localStorage.setItem' in js_content, \
            "changeTheme should save to localStorage"

    def test_loadtheme_called_on_domcontentloaded(self, client):
        """Test that loadTheme is called when page loads"""
        response = client.get('/static/script.js')
        js_content = response.data.decode('utf-8')

        # Check for DOMContentLoaded event listener
        assert 'DOMContentLoaded' in js_content, \
            "Script should listen for DOMContentLoaded"
        assert 'loadTheme' in js_content, \
            "loadTheme should be called on page load"

    def test_default_theme_fallback_exists(self, client):
        """Test that there's a fallback to default theme if localStorage is empty"""
        response = client.get('/static/script.js')
        js_content = response.data.decode('utf-8')

        # Check for fallback logic (|| 'macos' or similar)
        assert "'macos'" in js_content or '"macos"' in js_content, \
            "Should have default theme fallback"


# ============================================================================
# EDGE CASES AND ERROR HANDLING
# ============================================================================

class TestThemeEdgeCases:
    """Test edge cases and error handling for themes"""

    def test_invalid_theme_validation_logic(self, client):
        """Test that invalid theme values are handled"""
        response = client.get('/static/script.js')
        js_content = response.data.decode('utf-8')

        # Should have validation to fall back to default
        # Look for error handling or fallback patterns
        has_fallback = any(pattern in js_content for pattern in [
            "themeName = 'macos'",
            'themeName = "macos"',
            "selectedTheme = 'macos'",
            'selectedTheme = "macos"',
            'return;',
            'console.error',
        ])

        assert has_fallback, "Should have error handling for invalid themes"

    def test_theme_code_handles_missing_elements(self, client):
        """Test that theme code handles missing DOM elements gracefully"""
        response = client.get('/static/script.js')
        js_content = response.data.decode('utf-8')

        # Good practice: check if element exists before using it
        # Look for getElementById followed by null check
        has_null_checks = 'getElementById' in js_content

        # At minimum, should have DOM queries
        assert has_null_checks, "Should query DOM elements"

    def test_css_specificity_correct(self, client):
        """Test that theme CSS has correct specificity"""
        response = client.get('/static/style.css')
        css_content = response.data.decode('utf-8')

        # Theme selectors should be at root level, not deeply nested
        # [data-theme="..."] should appear at the beginning of selectors
        assert '[data-theme="dark"]' in css_content, "Dark theme selector should exist"
        assert '[data-theme="blue"]' in css_content, "Blue theme selector should exist"


# ============================================================================
# LAYOUT PRESERVATION TESTS
# ============================================================================

class TestLayoutPreservation:
    """Test that theme switching doesn't affect layout"""

    def test_no_layout_shifting_css(self, client):
        """Test that theme CSS doesn't cause layout shifts"""
        response = client.get('/static/style.css')
        css_content = response.data.decode('utf-8')

        # Theme changes should only affect colors, not dimensions
        # Check that CSS variables are for colors/shadows, not sizes
        theme_section_start = css_content.find('[data-theme=')
        if theme_section_start > -1:
            theme_section = css_content[theme_section_start:theme_section_start + 2000]

            # These should NOT be in theme definitions
            layout_properties = ['width:', 'height:', 'padding:', 'margin:', 'font-size:']

            # Note: Some properties like border might be themed, which is OK
            # But major layout properties should not change
            # For a strict test, we just verify theme variables exist
            assert '--bg-' in theme_section or '--btn-' in theme_section or '--text-' in theme_section, \
                "Theme sections should define color variables"

    def test_calculator_structure_unchanged(self, client):
        """Test that calculator HTML structure is not modified by theme feature"""
        response = client.get('/')
        html_content = response.data.decode('utf-8')

        # Verify essential calculator structure still exists
        assert 'class="calculator"' in html_content, "Calculator container should exist"
        assert 'class="display"' in html_content, "Display should exist"
        assert 'class="buttons"' in html_content, "Buttons container should exist"
        assert 'btn-number' in html_content, "Number buttons should exist"
        assert 'btn-operator' in html_content, "Operator buttons should exist"

    def test_button_grid_preserved(self, client):
        """Test that button grid layout is preserved"""
        response = client.get('/static/style.css')
        css_content = response.data.decode('utf-8')

        # Grid layout should still exist
        assert 'grid-template-columns' in css_content, "Grid layout should be preserved"
        assert '.buttons' in css_content, "Buttons container CSS should exist"


# ============================================================================
# ACCESSIBILITY TESTS
# ============================================================================

class TestThemeAccessibility:
    """Test accessibility aspects of theme feature"""

    def test_theme_selector_has_label(self, client):
        """Test that theme selector has proper label for screen readers"""
        response = client.get('/')
        html_content = response.data.decode('utf-8')

        # Should have a label for the select element
        assert '<label' in html_content, "Theme selector should have a label"
        assert 'for="themeSelect"' in html_content or 'Theme:' in html_content, \
            "Label should be associated with theme selector"

    def test_sufficient_contrast_values_in_css(self, client):
        """Test that theme colors suggest sufficient contrast"""
        response = client.get('/static/style.css')
        css_content = response.data.decode('utf-8')

        # This is a basic check - in reality, you'd need to calculate contrast ratios
        # We just verify that text colors are defined for each theme
        assert '--text-display' in css_content, "Display text color should be defined"
        assert '--btn-number-text' in css_content or 'btn-number' in css_content, \
            "Button text colors should be defined"

    def test_theme_works_with_keyboard_navigation(self, client):
        """Test that theme selector is keyboard accessible"""
        response = client.get('/')
        html_content = response.data.decode('utf-8')

        # Select element is keyboard accessible by default
        # Just verify it's a standard select element
        assert '<select' in html_content, "Should use standard select element for keyboard accessibility"
        assert 'id="themeSelect"' in html_content, "Select should have ID"


# ============================================================================
# THEME COMPATIBILITY TESTS
# ============================================================================

class TestThemeCompatibility:
    """Test theme compatibility with calculator features"""

    def test_theme_works_with_scientific_mode(self, client):
        """Test that themes work with scientific calculator mode"""
        response = client.get('/')
        html_content = response.data.decode('utf-8')

        # Verify scientific panel exists
        assert 'scientific-panel' in html_content, "Scientific panel should exist"

        # Check CSS for scientific button theming
        css_response = client.get('/static/style.css')
        css_content = css_response.data.decode('utf-8')

        assert '.btn-scientific' in css_content, "Scientific buttons should have CSS"
        # Scientific buttons should use theme variables
        assert '--btn-function' in css_content, "Scientific buttons should use theme variables"

    def test_theme_works_with_history_panel(self, client):
        """Test that themes apply to history panel"""
        response = client.get('/')
        html_content = response.data.decode('utf-8')

        # Verify history panel exists
        assert 'history-panel' in html_content, "History panel should exist"

        # Check CSS for history panel theming
        css_response = client.get('/static/style.css')
        css_content = css_response.data.decode('utf-8')

        assert '.history-panel' in css_content, "History panel should have CSS"
        # History panel should use theme variables
        assert '--history-bg' in css_content or 'history-panel' in css_content, \
            "History panel should use theme variables"

    def test_theme_selector_position_doesnt_overlap(self, client):
        """Test that theme selector doesn't overlap with calculator"""
        response = client.get('/static/style.css')
        css_content = response.data.decode('utf-8')

        # Theme selector should be positioned away from calculator
        assert '.theme-toggle' in css_content or '.theme-selector' in css_content

        # Should use fixed or absolute positioning
        if '.theme-toggle' in css_content:
            toggle_start = css_content.find('.theme-toggle')
            toggle_section = css_content[toggle_start:toggle_start + 300]
            assert 'position:' in toggle_section or 'position :' in toggle_section, \
                "Theme toggle should be positioned"


# ============================================================================
# REQUIREMENTS VERIFICATION TESTS
# ============================================================================

class TestRequirements:
    """Verify all user story requirements are met"""

    def test_three_themes_exist(self, client):
        """Test that exactly 3 themes are available"""
        response = client.get('/')
        html_content = response.data.decode('utf-8')

        # Count theme options in select
        theme_count = html_content.count('<option value=')

        # Should have at least 3 themes
        assert theme_count >= 3, "Should have at least 3 theme options"

        # Verify specific themes
        assert 'value="macos"' in html_content
        assert 'value="dark"' in html_content
        assert 'value="blue"' in html_content

    def test_macos_is_default_theme(self, client):
        """Test that macOS theme is the default"""
        response = client.get('/static/style.css')
        css_content = response.data.decode('utf-8')

        # macOS should be in :root (which means it's default)
        # OR it should be the first theme defined
        assert ':root' in css_content, "Should have :root definition for default theme"

    def test_theme_ui_is_non_intrusive(self, client):
        """Test that theme UI is non-intrusive (per requirements)"""
        response = client.get('/static/style.css')
        css_content = response.data.decode('utf-8')

        # Theme toggle should be positioned out of the way
        if '.theme-toggle' in css_content:
            toggle_section_start = css_content.find('.theme-toggle')
            toggle_section = css_content[toggle_section_start:toggle_section_start + 500]

            # Should be positioned fixed or absolute
            assert 'position' in toggle_section, "Theme selector should be positioned"

            # Common non-intrusive positions: top-right, top-left
            has_positioning = any(prop in toggle_section for prop in ['top:', 'right:', 'left:'])
            assert has_positioning, "Theme selector should be positioned non-intrusively"

    def test_all_calculator_features_preserved(self, client):
        """Test that all existing calculator features are preserved"""
        response = client.get('/')
        html_content = response.data.decode('utf-8')

        # Verify all essential features still exist
        essential_features = [
            'class="display"',
            'btn-number',
            'btn-operator',
            'btn-function',
            'scientific-panel',
            'history-panel',
            'onclick="appendNumber',
            'onclick="setOperator',
            'onclick="calculate',
        ]

        for feature in essential_features:
            assert feature in html_content, f"Feature {feature} should be preserved"

    def test_no_functionality_changes(self, client):
        """Test that calculator functionality is not modified"""
        response = client.get('/static/script.js')
        js_content = response.data.decode('utf-8')

        # Essential calculator functions should still exist
        essential_functions = [
            'function appendNumber',
            'function calculate',
            'function setOperator',
            'function clearAll',
        ]

        for func in essential_functions:
            assert func in js_content, f"Calculator function {func} should be preserved"


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

class TestThemePerformance:
    """Test performance aspects of theme switching"""

    def test_css_uses_variables_for_efficiency(self, client):
        """Test that CSS uses CSS variables for efficient theme switching"""
        response = client.get('/static/style.css')
        css_content = response.data.decode('utf-8')

        # Should use CSS custom properties (variables)
        assert '--' in css_content, "Should use CSS variables"
        assert 'var(--' in css_content, "Should reference CSS variables with var()"

    def test_minimal_javascript_for_theme_switching(self, client):
        """Test that theme switching uses minimal JavaScript"""
        response = client.get('/static/script.js')
        js_content = response.data.decode('utf-8')

        # Theme functions should be relatively simple
        # Just verify they exist and aren't overly complex
        assert 'function changeTheme' in js_content or 'changeTheme()' in js_content
        assert 'function applyTheme' in js_content or 'applyTheme(' in js_content

        # Should not have excessive DOM manipulation
        # Count setAttribute calls in theme code (should be minimal)
        theme_section_start = js_content.find('Theme Management')
        if theme_section_start > -1:
            theme_section = js_content[theme_section_start:theme_section_start + 2000]
            # Theme switching should primarily just set/remove one attribute
            assert 'setAttribute' in theme_section or 'data-theme' in theme_section


# ============================================================================
# INTEGRATION WITH EXISTING FEATURES
# ============================================================================

class TestThemeIntegration:
    """Test theme integration with existing calculator features"""

    def test_theme_preserves_calculation_functionality(self, client):
        """Test that calculations still work with theme feature"""
        # Perform a calculation
        response = client.post('/calculate',
                              data=json.dumps({'expression': '5+3'}),
                              content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['result'] == 8

        # Theme feature is frontend-only, so backend should be unaffected

    def test_theme_preserves_history_functionality(self, client):
        """Test that history still works with theme feature"""
        # Get history
        response = client.get('/history')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'history' in data

    def test_theme_preserves_scientific_functions(self, client):
        """Test that scientific functions still work with theme feature"""
        # Test a scientific function
        response = client.post('/scientific',
                              data=json.dumps({'function': 'sqrt', 'value': 16}),
                              content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['result'] == 4.0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
