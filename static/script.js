/**
 * macOS Calculator JavaScript
 * Handles calculator logic, theme switching, and history management
 */

// Calculator state
let currentValue = '0';
let previousValue = null;
let operation = null;
let shouldResetDisplay = false;

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

    // Display history in reverse order (most recent first)
    const historyHTML = [...history].reverse().map(item => {
        return `
            <div class="history-item" onclick="loadFromHistory('${item.result}')">
                <div class="history-expression">${formatExpression(item.expression)}</div>
                <div class="history-result">${formatNumber(item.result)}</div>
            </div>
        `;
    }).join('');

    historyList.innerHTML = historyHTML;
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
    }
});
