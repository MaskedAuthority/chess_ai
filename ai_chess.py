import chess
import chess.pgn
import google.generativeai as genai
import os
from openai import OpenAI
import re
import time

def display_board(board):
    print(board)

def get_player_move(board):
    while True:
        try:
            move_str = input("Enter your move (White, e.g., e4): ")
            move = board.parse_san(move_str)
            if move in board.legal_moves:
                return move
            else:
                print("Invalid move. Please try again.")
        except ValueError:
            print("Invalid move format. Use algebraic notation (e.g., e4).")

def get_black_move(board, move_text):
    """Gets Black's move from the move_text parameter."""
    try:
        move = board.parse_san(move_text)
        if move in board.legal_moves:
            return move
        else:
            print(f"Invalid move: {move_text}")
            return None
    except (ValueError, chess.InvalidMoveError) as e:
        print(f"Error parsing move: {e}")
        return None

def get_ollama_move(board, ollama_client, model_name):
    """Gets a move from the Ollama model with improved prompting and fallback strategies."""
    try:
        # Get legal moves in both UCI and SAN format
        legal_moves_uci = [move.uci() for move in board.legal_moves]
        legal_moves_san = [board.san(move) for move in board.legal_moves]
        
        # Create a more detailed and structured prompt
        prompt = (
            f"You are playing as White in a chess game.\n\n"
            f"Current board state (FEN): {board.fen()}\n\n"
            f"Legal moves in UCI format: {', '.join(legal_moves_uci)}\n"
            f"Legal moves in SAN format: {', '.join(legal_moves_san)}\n\n"
            f"Attempt to win the game of chess do not just copy Blacks moves. Use opening and closing strategies to gain a checkmate of Black"
            f"Provide your next move. Your response must be EXACTLY ONE of the legal SAN format moves listed above. "
            f"Output ONLY the move with no explanations or additional text. For example: 'e4' or 'Nf3' or 'O-O'."
        )
        
        # Get the model's response
        chat_completion = ollama_client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "You are a chess engine that outputs only legal chess moves in standard algebraic notation (SAN). Never explain your reasoning."},
                {"role": "user", "content": prompt}
            ]
        )
        
        raw_response = chat_completion.choices[0].message.content.strip()
        print(f"Ollama (raw response): {raw_response}")
        
        # Try to extract just the move if other text is present
        move_text = extract_move(raw_response, legal_moves_san)
        
        # If we couldn't extract a valid move, try using UCI format as fallback
        if move_text is None or move_text not in legal_moves_san:
            move_text = extract_move(raw_response, legal_moves_uci)
            if move_text in legal_moves_uci:
                # Convert UCI to SAN
                move = chess.Move.from_uci(move_text)
                move_text = board.san(move)
        
        # If we still don't have a valid move, try parsing as SAN
        try:
            move = board.parse_san(move_text)
            if move in board.legal_moves:
                return move
        except (ValueError, chess.InvalidMoveError):
            pass
            
        # Last resort: If we couldn't get a valid move, pick a random legal move
        if move_text not in legal_moves_san:
            print(f"Ollama suggested invalid move: '{move_text}'. Picking a random legal move instead.")
            import random
            move = random.choice(list(board.legal_moves))
            print(f"Random move selected: {board.san(move)}")
            return move
        else:
            # Found a valid move in SAN format
            return board.parse_san(move_text)

    except Exception as e:
        print(f"Error getting Ollama move: {e}")
        # Fallback to random move
        import random
        move = random.choice(list(board.legal_moves))
        print(f"Exception occurred. Random move selected: {board.san(move)}")
        return move

def extract_move(text, legal_moves):
    """Try to extract a legal chess move from text."""
    # First, check if the entire text is a legal move
    if text in legal_moves:
        return text
    
    # Then check if any of the legal moves are contained in the text
    for move in legal_moves:
        if move in text:
            return move
    
    # Look for words that might be moves
    words = re.findall(r'\b\w+(?:-\w+)*\b', text)
    for word in words:
        if word in legal_moves:
            return word
    
    # Check for specific patterns (like O-O, O-O-O)
    castling_matches = re.findall(r'O-O(?:-O)?', text)
    for match in castling_matches:
        if match in legal_moves:
            return match
    
    return None

def main():    
    genai.configure(api_key="AIzaSyB8yVETCPRHb4Eag9h3yI_lCZLH_-YRZA0")
    gemini_model = genai.GenerativeModel("gemini-2.0-flash")  # Or your preferred model
    
    ollama_client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
    ollama_model_name = "openhermes:latest"

    board = chess.Board()
    game = chess.pgn.Game()
    node = game

    move_count = 0
    max_moves = 100  # Safety to prevent infinite games

    while not board.is_game_over() and move_count < max_moves:
        # add a sleep for 5 seconds
        time.sleep(1)
        
        display_board(board)
        move_count += 1

        if board.turn == chess.WHITE:
            move = get_ollama_move(board, ollama_client, ollama_model_name)
            if move is None:
                print("Ollama made an invalid move. Ending game.")
                break

            print(f"White's move (Ollama): {board.san(move)}")
            board.push(move)
            node = node.add_variation(move)

        else:  # Black's turn (Gemini)
            legal_moves = [board.san(move) for move in board.legal_moves]
            prompt = (
                f"You are playing as Black in a chess game.\n\n"
                f"Current board state (FEN): {board.fen()}\n\n"
                f"Legal moves in SAN format: {', '.join(legal_moves)}\n\n"
                f"Provide your next move. Your response must be EXACTLY ONE of the legal moves listed above. "
                f"Output ONLY the move with no explanations or additional text. For example: 'e5' or 'Nf6' or 'O-O'."
            )
            response = gemini_model.generate_content(prompt)

            if not response.text:
                print("Gemini returned an empty response. Ending game.")
                break

            move_text = response.text.strip()  # Remove extra spaces
            print(f"Gemini (raw response): {move_text}")  # Debugging
            
            # Try to extract just the move if other text is present
            move_text = extract_move(move_text, legal_moves)
            
            try:
                move = board.parse_san(move_text)
                if move in board.legal_moves:
                    print(f"Black's move (Gemini): {board.san(move)}")
                    board.push(move)
                    node = node.add_variation(move)
                else:
                    print(f"Gemini made an invalid move: {move_text}. Ending game.")
                    break
            except (ValueError, chess.InvalidMoveError, TypeError) as e:
                print(f"Error with Gemini's move: {e}")
                # Fallback to random move for Gemini too
                import random
                move = random.choice(list(board.legal_moves))
                print(f"Random move selected for Gemini: {board.san(move)}")
                board.push(move)
                node = node.add_variation(move)

    display_board(board)  # Display final board state

    # Game Over Conditions
    if board.is_checkmate():
        winner = "White" if board.turn == chess.BLACK else "Black"
        print(f"Checkmate! {winner} wins!")
    elif board.is_stalemate():
        print("Stalemate!")
    elif board.is_insufficient_material():
        print("Insufficient material!")
    elif board.is_seventy_five_moves():
        print("75-move rule!")
    elif board.is_fivefold_repetition():
        print("Fivefold repetition!")
    elif move_count >= max_moves:
        print(f"Game stopped after {max_moves} moves.")
    else:
        print("Game Over")

    game.headers["Result"] = board.result()  # Add result to PGN
    game.headers["White"] = "Ollama"
    game.headers["Black"] = "Gemini"
    game.headers["Date"] = "????.??.??"

    with open("game.pgn", "w") as f:
        print(game, file=f)

if __name__ == "__main__":
    main()
