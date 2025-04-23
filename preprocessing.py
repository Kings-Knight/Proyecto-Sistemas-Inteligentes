import pandas as pd

# Define the path to the CSV file
data_path = "chessData.csv"  # Ensure the file is in the same directory as the script

# Load the dataset into a Pandas DataFrame
df = pd.read_csv(data_path)

# Function to process the Evaluation column efficiently
def process_evaluation(value):
    if isinstance(value, str) and value.startswith("#"):
        return 10000 if "#-" not in value else -10000
    try:
        return float(value)  # Convert normal evaluations to float
    except ValueError:
        return None  # Handle unexpected values gracefully

# Apply function to update the Evaluation column efficiently
df["Evaluation"] = df["Evaluation"].map(process_evaluation)

# Mapping of chess pieces to numeric values
piece_map = {
    'K': 6, 'Q': 5, 'R': 4, 'B': 3, 'N': 2, 'P': 1,
    'k': -6, 'q': -5, 'r': -4, 'b': -3, 'n': -2, 'p': -1
}

# Function to parse FEN and extract features
def parse_fen(fen):
    board_part, turn, castling, en_passant, halfmove, fullmove = fen.split()
    
    # Convert board state to 64 columns
    board_matrix = []
    for row in board_part.split('/'):
        for char in row:
            if char.isdigit():
                board_matrix.extend([0] * int(char))
            else:
                board_matrix.append(piece_map[char])
    
    # Side to move (1 for White, 0 for Black)
    side_to_move = 1 if turn == 'w' else 0
    
    # Castling rights (King-side = 1, Queen-side = 2, Both = 3, None = 0)
    white_castle = (1 if 'K' in castling else 0) + (2 if 'Q' in castling else 0)
    black_castle = (1 if 'k' in castling else 0) + (2 if 'q' in castling else 0)
    
    # Convert en passant target square to numeric index (1-64) or 0 if not applicable
    if en_passant != "-":
        file = ord(en_passant[0]) - ord('a')
        rank = int(en_passant[1]) - 1
        en_passant_square = rank * 8 + file + 1  # Convert to 1-based index
    else:
        en_passant_square = 0
    
    return board_matrix + [side_to_move, white_castle, black_castle, en_passant_square, int(halfmove), int(fullmove)]

# Apply FEN parsing to dataframe
df_parsed = df["FEN"].apply(parse_fen)
columns = [f"Square_{i}" for i in range(64)] + ["SideToMove", "WhiteCastle", "BlackCastle", "EnPassantSquare", "HalfmoveClock", "FullmoveCounter"]
df_expanded = pd.DataFrame(df_parsed.tolist(), columns=columns)

# Merge new dataframe with original
df = pd.concat([df_expanded, df], axis=1)

# Drop the original FEN column as it's now encoded
df.drop(columns=["FEN"], inplace=True)

# Save the processed DataFrame to a new CSV file
df.to_csv("processed_chessData.csv", index=False)

# Display the first few rows
print(df.head())
