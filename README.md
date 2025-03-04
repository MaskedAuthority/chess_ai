# AI Chess Battle: Ollama vs Gemini

![Chess AI Battle](https://img.shields.io/badge/Chess-AI%20Battle-blue)
![Python](https://img.shields.io/badge/Python-3.7%2B-yellow)
![License](https://img.shields.io/badge/License-MIT-green)

A Python application that creates an automated chess match between two AI models: **Ollama** (White) vs **Gemini** (Black).

## 🎮 Demo

```
  a b c d e f g h
8 r n b q k b n r
7 p p p p p p p p
6 . . . . . . . .
5 . . . . . . . .
4 . . . . P . . .
3 . . . . . . . .
2 P P P P . P P P
1 R N B Q K B N R

White's move (Ollama): e4
Gemini (raw response): e5
Black's move (Gemini): e5

  a b c d e f g h
8 r n b q k b n r
7 p p p p . p p p
6 . . . . . . . .
5 . . . . p . . .
4 . . . . P . . .
3 . . . . . . . .
2 P P P P . P P P
1 R N B Q K B N R
```

## ✨ Features

- 🤖 **AI vs AI**: Watch two AI models battle it out in chess
- 🧠 **Ollama Integration**: Uses local Ollama models as White
- ☁️ **Gemini API**: Leverages Google's Gemini API as Black
- 🛡️ **Error Handling**: Robust fallback strategies for invalid moves
- 📝 **PGN Export**: Saves games in standard chess notation

## 🚀 Quick Start

### Prerequisites

- Python 3.7+
- [Ollama](https://ollama.ai/) running locally
- Google AI API key for Gemini

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/ai-chess-battle.git
cd ai-chess-battle

# Install dependencies
pip install chess google-generativeai openai
```

### Configuration

1. Replace the Google API key in the code:
   ```python
   genai.configure(api_key="YOUR_GOOGLE_API_KEY")
   ```

2. Ensure Ollama is running locally (default: http://localhost:11434)

3. Optionally modify the Ollama model:
   ```python
   ollama_model_name = "openhermes:latest"  # Use your preferred model
   ```

### Run

```bash
python main.py
```

## 🔧 How It Works

1. The game initializes a chess board and sets up PGN recording
2. Ollama (White) and Gemini (Black) take turns making moves
3. Each AI is prompted with the current board state and legal moves
4. Moves are validated and applied to the board
5. The game continues until checkmate, stalemate, or move limit
6. Results are saved to `game.pgn`

## 📋 Technical Details

### Ollama Move Generation

```python
# Structured prompt for move generation
prompt = (
    f"You are playing as White in a chess game.\n\n"
    f"Current board state (FEN): {board.fen()}\n\n"
    f"Legal moves in UCI format: {', '.join(legal_moves_uci)}\n"
    f"Legal moves in SAN format: {', '.join(legal_moves_san)}\n\n"
    f"Provide your next move. Your response must be EXACTLY ONE of the legal SAN format moves listed above. "
    f"Output ONLY the move with no explanations or additional text. For example: 'e4' or 'Nf3' or 'O-O'."
)
```

### Gemini Move Generation

```python
prompt = (
    f"You are playing as Black in a chess game.\n\n"
    f"Current board state (FEN): {board.fen()}\n\n"
    f"Legal moves in SAN format: {', '.join(legal_moves)}\n\n"
    f"Provide your next move. Your response must be EXACTLY ONE of the legal moves listed above. "
    f"Output ONLY the move with no explanations or additional text. For example: 'e5' or 'Nf6' or 'O-O'."
)
```

## 📊 Output

The application produces:
- Console output showing the board and moves in real-time
- A `game.pgn` file containing the full game in standard notation

## 🔍 Future Improvements

- [ ] Web interface for game visualization
- [ ] Support for additional AI models
- [ ] Time control simulation
- [ ] Opening book integration
- [ ] Game analysis tools

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [python-chess](https://python-chess.readthedocs.io/) library
- [Ollama](https://ollama.ai/) project
- [Google Generative AI](https://ai.google.dev/) (Gemini)

---

Made with ❤️ by [Your Name]
