/**
 * macOS Calculator JavaScript
 * Handles calculator logic, theme switching, and history management
 *
 * SECURITY NOTES:
 * - Uses textContent instead of innerHTML to prevent XSS
 * - DOM manipulation prevents injection attacks
 * - Event listeners instead of inline onclick handlers
 * - Input validation on client side (server validates too)
 */

// Calculator state
let currentValue = '0';
let previousValue = null;
let operation = null;
let shouldResetDisplay = false;

// Scientific calculator state
let scientificMode = false;
let angleMode = 'deg'; // 'deg' or 'rad'
let memory = 0;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadTheme();
    loadHistory();
});

/**
 * Theme Management
 */
function toggleTheme() {
    const body = document.body;
    const themeBtn = document.getElementById('themeBtn');
    const currentTheme = body.getAttribute('data-theme');

    if (currentTheme === 'dark') {
        body.removeAttribute('data-theme');
        themeBtn.innerHTML = '<span class="theme-icon">☀️</span>';
        localStorage.setItem('theme', 'light');
    } else {
        body.setAttribute('data-theme', 'dark');
        themeBtn.innerHTML = '<span class="theme-icon">🌙</span>';
        localStorage.setItem('theme', 'dark');
    }
}

function loadTheme() {
    const savedTheme = localStorage.getItem('theme');
    const themeBtn = document.getElementById('themeBtn');

    if (savedTheme === 'dark') {
        document.body.setAttribute('data-theme', 'dark');
        themeBtn.innerHTML = '<span class="theme-icon">🌙</span>';
    } else {
        themeBtn.innerHTML = '<span class="theme-icon">☀️</span>';
    }
}

/**
 * Display Functions
 */
function updateDisplay(value = currentValue) {
    const display = document.getElementById('display');
    // Format large numbers
    if (value.length > 9) {
        display.style.fontSize = '40px';
    } else if (value.length > 7) {
        display.style.fontSize = '48px';
    } else {
        display.style.fontSize = '56px';
    }
    display.textContent = value;
}

/**
 * Calculator Operations
 */
function appendNumber(num) {
    if (shouldResetDisplay) {
        currentValue = num;
        shouldResetDisplay = false;
    } else {
        if (currentValue === '0' && num !== '.') {
            currentValue = num;
        } else if (num === '.' && currentValue.includes('.')) {
            return; // Prevent multiple decimals
        } else {
            currentValue += num;
        }
    }
    updateDisplay();
}

function clearAll() {
    currentValue = '0';
    previousValue = null;
    operation = null;
    shouldResetDisplay = false;
    updateDisplay();
    clearOperatorHighlight();
}

function toggleSign() {
    if (currentValue === '0') return;
    currentValue = String(parseFloat(currentValue) * -1);
    updateDisplay();
}

function percentage() {
    currentValue = String(parseFloat(currentValue) / 100);
    updateDisplay();
}

function setOperator(op) {
    if (previousValue !== null && !shouldResetDisplay) {
        calculate();
    }
    operation = op;
    previousValue = currentValue;
    shouldResetDisplay = true;
    highlightOperator(op);
}

function highlightOperator(op) {
    clearOperatorHighlight();
    const operators = {
        '+': '+',
        '-': '−',
        '*': '×',
        '/': '÷'
    };
    const buttons = document.querySelectorAll('.btn-operator');
    buttons.forEach(btn => {
        if (btn.textContent === operators[op]) {
            btn.classList.add('active');
        }
    });
}

function clearOperatorHighlight() {
    const buttons = document.querySelectorAll('.btn-operator');
    buttons.forEach(btn => btn.classList.remove('active'));
}

async function calculate() {
    if (operation === null || previousValue === null) {
        return;
    }

    // Handle power operation separately
    if (operation === '^') {
        try {
            const result = await callScientificAPI('power', {
                base: parseFloat(previousValue),
                exponent: parseFloat(currentValue)
            });
            currentValue = String(result);
            updateDisplay();
        } catch (error) {
            displayError(error.message || 'Calculation error');
        }
        operation = null;
        previousValue = null;
        shouldResetDisplay = true;
        clearOperatorHighlight();
        return;
    }

    const expression = `${previousValue}${operation}${currentValue}`;

    try {
        const response = await fetch('/calculate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ expression })
        });

        const data = await response.json();

        if (response.ok) {
            currentValue = String(data.result);
            updateDisplay();
            updateHistoryDisplay(data.history);
        } else {
            displayError(data.error);
        }
    } catch (error) {
        displayError('Network error');
    }

    operation = null;
    previousValue = null;
    shouldResetDisplay = true;
    clearOperatorHighlight();
}

function displayError(message) {
    const display = document.getElementById('display');
    display.textContent = message;
    setTimeout(() => {
        currentValue = '0';
        updateDisplay();
    }, 2000);
}

/**
 * History Management
 */
async function loadHistory() {
    try {
        const response = await fetch('/history');
        const data = await response.json();
        updateHistoryDisplay(data.history);
    } catch (error) {
        console.error('Failed to load history:', error);
    }
}

function updateHistoryDisplay(history) {
    const historyList = document.getElementById('history-list');

    if (!history || history.length === 0) {
        historyList.innerHTML = '<p class="empty-history">No calculations yet</p>';
        return;
    }

    // SECURITY: Clear existing content to prevent XSS
    historyList.innerHTML = '';

    // Display history in reverse order (most recent first)
    // SECURITY: Use DOM manipulation instead of innerHTML to prevent XSS
    [...history].reverse().forEach(item => {
        const historyItem = document.createElement('div');
        historyItem.className = 'history-item';

        // SECURITY: Set text content (not innerHTML) to prevent XSS injection
        const expressionDiv = document.createElement('div');
        expressionDiv.className = 'history-expression';
        expressionDiv.textContent = formatExpression(item.expression);

        const resultDiv = document.createElement('div');
        resultDiv.className = 'history-result';
        resultDiv.textContent = formatNumber(item.result);

        historyItem.appendChild(expressionDiv);
        historyItem.appendChild(resultDiv);

        // SECURITY: Use event listener instead of inline onclick
        historyItem.addEventListener('click', () => loadFromHistory(item.result));

        historyList.appendChild(historyItem);
    });
}

function formatExpression(expr) {
    return expr
        .replace(/\*/g, '×')
        .replace(/\//g, '÷')
        .replace(/-/g, '−');
}

function formatNumber(num) {
    // Format number for display
    const numStr = String(num);
    if (numStr.length > 12) {
        return parseFloat(num).toExponential(6);
    }
    return num;
}

function loadFromHistory(result) {
    // SECURITY: Validate result is a number before using it
    if (typeof result !== 'number' || isNaN(result) || !isFinite(result)) {
        console.error('Invalid result from history:', result);
        return;
    }
    currentValue = String(result);
    updateDisplay();
    shouldResetDisplay = true;
}

async function clearHistory() {
    try {
        const response = await fetch('/clear-history', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });

        if (response.ok) {
            updateHistoryDisplay([]);
        }
    } catch (error) {
        console.error('Failed to clear history:', error);
    }
}

/**
 * Scientific Functions
 */
function toggleScientificMode() {
    scientificMode = !scientificMode;
    const scientificPanel = document.querySelector('.scientific-panel');
    const modeBtn = document.getElementById('sciModeBtn');

    if (scientificMode) {
        scientificPanel.classList.add('visible');
        modeBtn.textContent = 'Basic';
    } else {
        scientificPanel.classList.remove('visible');
        modeBtn.textContent = 'Scientific';
    }
}

function toggleAngleMode() {
    angleMode = angleMode === 'deg' ? 'rad' : 'deg';
    const angleModeBtn = document.getElementById('angleModeBtn');
    angleModeBtn.textContent = angleMode.toUpperCase();
}

// Convert degrees to radians if needed
function toRadians(value) {
    return angleMode === 'deg' ? value * (Math.PI / 180) : value;
}

// Convert radians to degrees if needed
function fromRadians(value) {
    return angleMode === 'deg' ? value * (180 / Math.PI) : value;
}

// Scientific function handlers
async function scientificFunction(func) {
    const value = parseFloat(currentValue);

    if (isNaN(value)) {
        displayError('Invalid input');
        return;
    }

    try {
        let result;
        switch(func) {
            case 'sin':
                result = await callScientificAPI('sin', toRadians(value));
                break;
            case 'cos':
                result = await callScientificAPI('cos', toRadians(value));
                break;
            case 'tan':
                result = await callScientificAPI('tan', toRadians(value));
                break;
            case 'asin':
                result = fromRadians(await callScientificAPI('asin', value));
                break;
            case 'acos':
                result = fromRadians(await callScientificAPI('acos', value));
                break;
            case 'atan':
                result = fromRadians(await callScientificAPI('atan', value));
                break;
            case 'log':
                result = await callScientificAPI('log', value);
                break;
            case 'ln':
                result = await callScientificAPI('ln', value);
                break;
            case 'exp':
                result = await callScientificAPI('exp', value);
                break;
            case 'sqrt':
                result = await callScientificAPI('sqrt', value);
                break;
            case 'square':
                result = await callScientificAPI('square', value);
                break;
            case 'reciprocal':
                result = await callScientificAPI('reciprocal', value);
                break;
            default:
                displayError('Unknown function');
                return;
        }

        currentValue = String(result);
        updateDisplay();
        shouldResetDisplay = true;
    } catch (error) {
        displayError(error.message || 'Calculation error');
    }
}

// Call backend for scientific calculations
async function callScientificAPI(func, value) {
    try {
        const response = await fetch('/scientific', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ function: func, value: value })
        });

        const data = await response.json();

        if (response.ok) {
            return data.result;
        } else {
            throw new Error(data.error || 'Calculation failed');
        }
    } catch (error) {
        throw new Error(error.message || 'Network error');
    }
}

// Insert constants
function insertConstant(constant) {
    if (constant === 'pi') {
        currentValue = String(Math.PI);
    } else if (constant === 'e') {
        currentValue = String(Math.E);
    }
    updateDisplay();
    shouldResetDisplay = true;
}

// Power function - sets up for x^y operation
function setPowerOperation() {
    if (previousValue !== null && !shouldResetDisplay) {
        calculate();
    }
    operation = '^';
    previousValue = currentValue;
    shouldResetDisplay = true;
}

// Memory functions
function memoryClear() {
    memory = 0;
    updateMemoryIndicator();
}

function memoryRecall() {
    currentValue = String(memory);
    updateDisplay();
    shouldResetDisplay = true;
}

function memoryAdd() {
    memory += parseFloat(currentValue);
    updateMemoryIndicator();
}

function memorySubtract() {
    memory -= parseFloat(currentValue);
    updateMemoryIndicator();
}

function updateMemoryIndicator() {
    const indicator = document.getElementById('memoryIndicator');
    if (indicator) {
        indicator.style.display = memory !== 0 ? 'block' : 'none';
    }
}

/**
 * Keyboard Support
 */
document.addEventListener('keydown', (event) => {
    const key = event.key;

    if (!isNaN(key)) {
        appendNumber(key);
    } else if (key === '.') {
        appendNumber('.');
    } else if (key === '+' || key === '-' || key === '*' || key === '/') {
        setOperator(key);
    } else if (key === 'Enter' || key === '=') {
        calculate();
    } else if (key === 'Escape' || key === 'c' || key === 'C') {
        clearAll();
    } else if (key === '%') {
        percentage();
    } else if (key === 'Backspace') {
        if (currentValue.length > 1) {
            currentValue = currentValue.slice(0, -1);
        } else {
            currentValue = '0';
        }
        updateDisplay();
    } else if (event.shiftKey && key === 'S') {
        toggleScientificMode();
    } else if (event.shiftKey && key === 'D') {
        toggleAngleMode();
    } else if (key === 'p') {
        insertConstant('pi');
    } else if (key === 'e' && !event.ctrlKey && !event.metaKey) {
        insertConstant('e');
    }
});
