# Security Documentation

## Overview
This document outlines the security measures implemented in the Scientific Calculator application to protect against common web vulnerabilities.

## Security Measures Implemented

### 1. Input Validation & Sanitization

#### Backend (app.py)
- **Safe Expression Evaluation**: Uses Abstract Syntax Tree (AST) parsing instead of dangerous `eval()` function
  - Whitelists only safe mathematical operators (Add, Sub, Mult, Div, USub, UAdd)
  - Prevents code injection attacks
  - Validates expression structure before evaluation

- **Input Type Validation**:
  - Validates all inputs are correct types (strings for expressions, numbers for values)
  - Prevents type confusion attacks

- **Length Limits**:
  - Expression length limited to 200 characters
  - History limited to 10 entries (with hard cap at 100)
  - Prevents session exhaustion and DoS attacks

- **Character Whitelisting**:
  - Only allows safe characters: `0123456789+-*/(). `
  - Blocks any potentially malicious characters

- **Complexity Limits**:
  - Maximum 50 parentheses pairs to prevent deeply nested expressions
  - Blocks suspicious patterns (e.g., repeated operators like `+++`)
  - Value range limits: |value| < 1e100

- **Mathematical Domain Validation**:
  - `asin/acos`: Requires values between -1 and 1
  - `log/ln`: Requires positive values
  - `sqrt`: Requires non-negative values
  - `reciprocal`: Prevents division by zero
  - `power`: Prevents 0^0, negative base with fractional exponent
  - Power function limits: |base| < 1e100, |exponent| < 1000

- **Output Validation**:
  - Checks for NaN (Not a Number)
  - Checks for Infinity/-Infinity
  - Validates results are finite numbers

#### Frontend (script.js)
- **Client-side Validation**: Additional validation before server requests
- **Number Validation**: Checks for NaN, Infinity, and range limits
- **Memory Overflow Protection**: Validates memory values don't overflow

### 2. Cross-Site Scripting (XSS) Prevention

- **DOM Manipulation**: Uses safe DOM methods instead of innerHTML
  - `textContent` instead of `innerHTML` for user data
  - `createElement()` and `appendChild()` for dynamic content

- **History Display**: Sanitizes all history entries
  - Creates elements programmatically
  - Uses event listeners instead of inline onclick (where possible)

- **Error Messages**: Generic error messages that don't reflect user input
  - Prevents reflected XSS attacks

### 3. LocalStorage Security (Theme Persistence)

**SECURITY HARDENING**: Theme selection uses localStorage with strict validation

- **Whitelist Validation**: Only allows predefined theme values (`macos`, `dark`, `blue`)
  - Prevents XSS if malicious script writes to localStorage
  - Theme values validated before reading from localStorage
  - Invalid values fallback to safe default (`macos`)

- **Defense in Depth**: Multiple validation layers
  - Validation when reading from localStorage (`loadTheme()`)
  - Validation when applying theme to DOM (`applyTheme()`)
  - Validation when user selects theme (`changeTheme()`)

- **Safe DOM Manipulation**: Uses `setAttribute()` only with validated values
  - Prevents injection of malicious attributes
  - Theme attribute values are strictly controlled

**Example Attack Prevention**:
```javascript
// Attacker tries to inject malicious theme via localStorage
localStorage.setItem('calculator-theme', '<img src=x onerror=alert(1)>');

// Our validation catches this and falls back to safe default
// Result: theme = 'macos' (safe default)
```

### 4. Rate Limiting

Protected endpoints (using Flask-Limiter):
- `/calculate`: 30 requests per minute
- `/scientific`: 30 requests per minute
- `/history`: 60 requests per minute
- `/clear-history`: 20 requests per minute
- Global limits: 200 per day, 50 per hour

Prevents:
- Brute force attacks
- Resource exhaustion
- Denial of Service (DoS)

### 5. Security Headers

Implemented via Flask-Talisman and custom middleware:

- **Content-Security-Policy (CSP)**: Restricts resource loading
  - `default-src 'self'`: Only load resources from same origin
  - `script-src 'self' 'unsafe-inline'`: Allow inline scripts (for onclick handlers)
  - `style-src 'self' 'unsafe-inline'`: Allow inline styles
  - `img-src 'self'`: Only load images from same origin

- **X-Content-Type-Options**: `nosniff`
  - Prevents MIME type sniffing attacks

- **X-XSS-Protection**: `1; mode=block`
  - Enables browser XSS filter

- **X-Frame-Options**: `DENY`
  - Prevents clickjacking attacks

- **Referrer-Policy**: `strict-origin-when-cross-origin`
  - Controls referrer information leakage

### 6. Session Security

- **HTTPOnly Cookies**: Prevents JavaScript access to session cookies
  - Protects against XSS-based session hijacking

- **SameSite Cookies**: Set to `Lax`
  - CSRF protection by restricting cross-site cookie sending

- **Session Timeout**: 1 hour (3600 seconds)
  - Limits window for session-based attacks

- **Secure Cookie Flag**: Configured for production (when HTTPS enabled)
  - Ensures cookies only sent over HTTPS

- **Random Secret Key**: Generated using `secrets.token_hex(16)`
  - Cryptographically secure session signing

### 7. Error Handling

- **Generic Error Messages**: Don't expose internal details
  - Users see: "Calculation failed"
  - Server logs: Actual error for debugging

- **No Stack Traces**: Production mode disables debug
  - Prevents information disclosure

- **Specific Domain Errors**: Safe to show mathematical errors
  - "Division by zero"
  - "Domain error: sqrt requires non-negative value"

### 8. Function Whitelisting

Scientific functions use explicit whitelist:
```python
allowed_functions = {
    'sin', 'cos', 'tan', 'asin', 'acos', 'atan',
    'log', 'ln', 'exp', 'sqrt', 'square', 'reciprocal', 'power'
}
```

Any function not in the whitelist is rejected.

## Security Vulnerabilities NOT Present

### ✅ SQL Injection
- **N/A**: Application uses session storage, no database queries

### ✅ Command Injection
- **N/A**: No system commands executed

### ✅ Path Traversal
- **Mitigated**: Uses Flask's `url_for()` for static files
- No user-controlled file paths

### ✅ Authentication Bypass
- **N/A**: No authentication required (public calculator)

### ✅ Sensitive Data Exposure
- **N/A**: No sensitive data stored
- Only calculation history in session
- Theme preference in localStorage (not sensitive)

### ✅ XML External Entity (XXE)
- **N/A**: No XML parsing

### ✅ Insecure Deserialization
- **N/A**: No serialized object handling
- JSON parsing only with type validation

## Production Security Checklist

When deploying to production, ensure:

- [ ] `FLASK_DEBUG=False` or not set
- [ ] `SESSION_COOKIE_SECURE=True` (requires HTTPS)
- [ ] `force_https=True` in Talisman configuration
- [ ] Use a production WSGI server (gunicorn, uWSGI)
- [ ] Enable HTTPS/TLS with valid certificate
- [ ] Set up proper logging (not just console)
- [ ] Configure firewall rules
- [ ] Regular dependency updates (`pip install --upgrade`)
- [ ] Monitor rate limit violations
- [ ] Set up error alerting

## Known Limitations

1. **Inline Event Handlers**: HTML uses onclick attributes
   - Required CSP `'unsafe-inline'` for scripts
   - Mitigation: All inputs validated server-side

2. **No CSRF Tokens**: Relies on SameSite cookies only
   - Acceptable for this use case (no state changes)
   - Consider adding tokens for production with multiple origins

3. **Client-side Storage**: Theme preference in localStorage
   - Not encrypted (but not sensitive data)
   - **MITIGATED**: Added strict whitelist validation to prevent XSS
   - Theme values validated on read, write, and apply operations

4. **Memory Storage**: Rate limiting uses in-memory storage
   - Resets on server restart
   - For production, consider Redis/Memcached

## Security Testing Performed

- ✅ Input validation for expressions
- ✅ XSS prevention in history display
- ✅ Rate limiting verification
- ✅ Domain validation for scientific functions
- ✅ Error handling (no stack traces)
- ✅ Session security configuration
- ✅ Mathematical edge cases (div by zero, sqrt(-1), etc.)
- ✅ Overflow protection (large numbers)
- ✅ Complex expression handling

## Reporting Security Issues

If you discover a security vulnerability:

1. **Do not** open a public issue
2. Contact the development team privately
3. Provide:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if available)

## References

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Flask Security Best Practices](https://flask.palletsprojects.com/en/latest/security/)
- [Content Security Policy](https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP)
- [Python AST Module](https://docs.python.org/3/library/ast.html)

## Version History

- **v1.1** (Current): Theme Feature Security Hardening
  - Added localStorage whitelist validation for themes
  - Defense-in-depth validation at multiple layers
  - Enhanced XSS prevention for theme switching
  - Updated security documentation

- **v1.0**: Initial security implementation
  - Safe expression evaluation
  - Rate limiting
  - Security headers
  - Input validation
  - XSS prevention
