# Candle Pytho

A cinematic ASCII candle renderer built with Python. It creates a glowing candle and an animated flame directly in your terminal using procedural rendering and ANSI colors.

## Features

- Animated flame with procedural flickering
- ASCII candle and flame rendering
- Terminal color support
- Optional no-color mode
- Adjustable animation frame rate
- Lightweight implementation using Python's standard library

## Requirements

- Python 3.9 or newer
- A terminal that supports ANSI colors for the full visual experience

## Getting Started

Clone the repository:

```bash
git clone https://github.com/ursadmin7/candle-pytho.git
cd candle-pytho
```

## Usage

Start the animated candle:

```bash
python candle.py
```

Run without colors:

```bash
python candle.py --no-color
```

Adjust the frame rate:

```bash
python candle.py --fps 30
```

Press `Ctrl+C` to stop the animation.

## Project Structure

```text
candle-pytho/
|-- candle.py
|-- tests/
|   `-- test_candle.py
|-- assets/
|-- docs/
|-- .gitignore
|-- LICENSE
|-- README.md
`-- requirements.txt
```

## Testing

Run the unit tests with:

```bash
python -m unittest discover -s tests -v
```

## Contributing

Contributions, suggestions, and improvements are welcome.

## License

See the LICENSE file for license details.
