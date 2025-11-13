# macOS-Themed Web Calculator

A beautiful web calculator inspired by the macOS calculator app, featuring light/dark themes and calculation history.

## Features

- 🎨 **macOS-inspired Design**: Authentic macOS calculator look and feel
- 🌓 **Light/Dark Theme**: Toggle between light and dark modes with persistent preference
- 📊 **Calculation History**: Keeps track of your last 5 calculations
- ⌨️ **Keyboard Support**: Use your keyboard for calculations
- 📱 **Responsive Design**: Works on desktop and mobile devices
- 🔢 **Basic Operations**: Addition, subtraction, multiplication, division
- 🎯 **Special Functions**: Percentage, sign toggle, clear

## Installation

1. Clone or navigate to this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Start the Flask server:
   ```bash
   python app.py
   ```

2. Open your browser and navigate to:
   ```
   http://localhost:5000
   ```

3. Start calculating!

## Keyboard Shortcuts

- **Numbers (0-9)**: Enter numbers
- **Operators (+, -, *, /)**: Perform operations
- **Enter or =**: Calculate result
- **Escape or C**: Clear all
- **%**: Percentage
- **Backspace**: Delete last digit

## Features Details

### Theme Switching
- Click the sun/moon button in the top-right corner to toggle themes
- Your preference is saved automatically using localStorage

### Calculation History
- Last 5 calculations are displayed in the history panel
- Click any history item to load that result
- Click "Clear" to remove all history
- History is stored in the session (non-persistent across browser sessions)

### Calculator Functions
- **AC**: Clear all (reset calculator)
- **±**: Toggle between positive and negative
- **%**: Convert to percentage (divide by 100)
- **÷**: Division
- **×**: Multiplication
- **−**: Subtraction
- **+**: Addition
- **=**: Calculate result

## Technical Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Styling**: Custom CSS with CSS Variables for theming
- **Session Management**: Flask sessions for history storage

## Project Structure

```
.
├── app.py                 # Flask application
├── requirements.txt       # Python dependencies
├── static/
│   ├── style.css         # Styles and themes
│   └── script.js         # Calculator logic and interactions
└── templates/
    └── index.html        # Main HTML template
```

## Security Notes

- The calculator uses Python's `eval()` for calculations but includes input validation
- Only numeric and operator characters are allowed in expressions
- Session-based history with secure secret key generation

## License

This project is provided as-is for educational and personal use.
