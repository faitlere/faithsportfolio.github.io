from __future__ import annotations

from typing import List, Tuple
import random
import re


class Piece:
    pos_x: int
    pos_y: int
    side: bool  # True for White and False for Black

    def __init__(self, pos_X: int, pos_Y: int, side_: bool):
        '''sets initial values'''
        self.pos_x = pos_X
        self.pos_y = pos_Y
        self.side = side_

    def copy(self) -> Piece:
        return type(self)(self.pos_x, self.pos_y, self.side)


class Queen(Piece):
    def __init__(self, pos_X: int, pos_Y: int, side_: bool):
        '''sets initial values by calling the constructor of Piece'''
        super().__init__(pos_X, pos_Y, side_)

    def can_reach(self, pos_X: int, pos_Y: int, B: 'Board') -> bool:
        '''
        checks if this queen can move to coordinates pos_X, pos_Y
        on board B according to rule [Rule1] and [Rule3] (see section Intro)
        Hint: use is_piece_at
        '''
        S, _ = B
        # Must stay on board
        if not (1 <= pos_X <= S and 1 <= pos_Y <= S):
            return False

        # Cannot stay in place
        if self.pos_x == pos_X and self.pos_y == pos_Y:
            return False

        # Cannot capture own piece
        if is_piece_at(pos_X, pos_Y, B):
            if piece_at(pos_X, pos_Y, B).side == self.side:
                return False

        dx = pos_X - self.pos_x
        dy = pos_Y - self.pos_y

        # Movement must be horizontal, vertical or diagonal
        if not (dx == 0 or dy == 0 or abs(dx) == abs(dy)):
            return False

        step_x = 0 if dx == 0 else (1 if dx > 0 else -1)
        step_y = 0 if dy == 0 else (1 if dy > 0 else -1)

        x, y = self.pos_x + step_x, self.pos_y + step_y
        while x != pos_X or y != pos_Y:
            if is_piece_at(x, y, B):
                return False
            x += step_x
            y += step_y

        return True

    def can_move_to(self, pos_X: int, pos_Y: int, B: 'Board') -> bool:
        '''
        checks if this queen can move to coordinates pos_X, pos_Y
        on board B according to all chess rules

        Hints:
        - firstly, check [Rule1] and [Rule3] using can_reach
        - secondly, check if result of move is capture using is_piece_at
        - if yes, find the piece captured using piece_at
        - thirdly, construct new board resulting from move
        - finally, to check [Rule4], use is_check on new board
        '''
        if not self.can_reach(pos_X, pos_Y, B):
            return False

        # Build new board and check Rule4 (self-check)
        new_board = self.move_to(pos_X, pos_Y, B)
        if is_check(self.side, new_board):
            return False
        return True

    def move_to(self, pos_X: int, pos_Y: int, B: 'Board') -> 'Board':
        '''
        returns new board resulting from move of this queen to coordinates pos_X, pos_Y on board B 
        assumes this move is valid according to chess rules
        '''
        S, pieces = B
        new_pieces: List[Piece] = []
        for p in pieces:
            # Skip captured piece (if any)
            if p.pos_x == pos_X and p.pos_y == pos_Y and p.side != self.side:
                continue
            if p is self:
                moved = Queen(pos_X, pos_Y, self.side)
                new_pieces.append(moved)
            else:
                new_pieces.append(p.copy())
        return (S, new_pieces)


class King(Piece):
    def __init__(self, pos_X: int, pos_Y: int, side_: bool):
        '''sets initial values by calling the constructor of Piece'''
        super().__init__(pos_X, pos_Y, side_)

    def can_reach(self, pos_X: int, pos_Y: int, B: 'Board') -> bool:
        '''checks if this king can move to coordinates pos_X, pos_Y on board B according to rule [Rule2] and [Rule3]'''
        S, _ = B
        if not (1 <= pos_X <= S and 1 <= pos_Y <= S):
            return False
        if self.pos_x == pos_X and self.pos_y == pos_Y:
            return False
        if is_piece_at(pos_X, pos_Y, B) and piece_at(pos_X, pos_Y, B).side == self.side:
            return False
        dx = abs(pos_X - self.pos_x)
        dy = abs(pos_Y - self.pos_y)
        return dx <= 1 and dy <= 1 and (dx != 0 or dy != 0)

    def can_move_to(self, pos_X: int, pos_Y: int, B: 'Board') -> bool:
        '''checks if this king can move to coordinates pos_X, pos_Y on board B according to all chess rules'''
        if not self.can_reach(pos_X, pos_Y, B):
            return False
        new_board = self.move_to(pos_X, pos_Y, B)
        # King cannot move into check
        if is_check(self.side, new_board):
            return False
        return True

    def move_to(self, pos_X: int, pos_Y: int, B: 'Board') -> 'Board':
        '''
        returns new board resulting from move of this king to coordinates pos_X, pos_Y on board B 
        assumes this move is valid according to chess rules
        '''
        S, pieces = B
        new_pieces: List[Piece] = []
        for p in pieces:
            # Skip captured piece (if any)
            if p.pos_x == pos_X and p.pos_y == pos_Y and p.side != self.side:
                continue
            if p is self:
                moved = King(pos_X, pos_Y, self.side)
                new_pieces.append(moved)
            else:
                new_pieces.append(p.copy())
        return (S, new_pieces)


Board = tuple[int, list[Piece]]


def location2index(loc: str) -> tuple[int, int]:
    '''converts chess location to corresponding x and y coordinates'''
    if not isinstance(loc, str) or len(loc) < 2:
        raise ValueError("Invalid location string")
    col = loc[0]
    row = loc[1:]
    if not ('a' <= col <= 'z'):
        raise ValueError("Column must be a lowercase letter a-z")
    if not row.isdigit():
        raise ValueError("Row must be a number")
    y = int(row)
    if not (1 <= y <= 26):
        raise ValueError("Row out of range 1..26")
    x = ord(col) - ord('a') + 1
    return (x, y)


def index2location(x: int, y: int) -> str:
    '''converts  pair of coordinates to corresponding location'''
    if not (1 <= x <= 26 and 1 <= y <= 26):
        raise ValueError("Coordinates out of range 1..26")
    col = chr(ord('a') + x - 1)
    return f"{col}{y}"


def is_piece_at(pos_X: int, pos_Y: int, B: Board) -> bool:
    '''checks if there is piece at coordinates pox_X, pos_Y of board B'''
    for p in B[1]:
        if p.pos_x == pos_X and p.pos_y == pos_Y:
            return True
    return False


def piece_at(pos_X: int, pos_Y: int, B: Board) -> Piece:
    '''
    returns the piece at coordinates pox_X, pos_Y of board B 
    assumes some piece at coordinates pox_X, pos_Y of board B is present
    '''
    for p in B[1]:
        if p.pos_x == pos_X and p.pos_y == pos_Y:
            return p
    raise ValueError("No piece at given position")


def _find_king(side: bool, B: Board) -> King:
    for p in B[1]:
        if isinstance(p, King) and p.side == side:
            return p
    raise ValueError("Board does not contain exactly one king for the given side")


def is_check(side: bool, B: Board) -> bool:
    '''
    checks if configuration of B is check for side
    Hint: use can_reach
    '''
    king = _find_king(side, B)
    kx, ky = king.pos_x, king.pos_y
    for p in B[1]:
        if p.side != side:
            if isinstance(p, Queen):
                if p.can_reach(kx, ky, B):
                    return True
            elif isinstance(p, King):
                if p.can_reach(kx, ky, B):
                    return True
    return False


def is_checkmate(side: bool, B: Board) -> bool:
    '''
    checks if configuration of B is checkmate for side

    Hints: 
    - use is_check
    - use can_move_to 
    '''
    if not is_check(side, B):
        return False

    S, pieces = B
    for p in pieces:
        if p.side == side:
            for x in range(1, S + 1):
                for y in range(1, S + 1):
                    if isinstance(p, Queen):
                        if p.can_move_to(x, y, B):
                            return False
                    elif isinstance(p, King):
                        if p.can_move_to(x, y, B):
                            return False
    return True


def is_stalemate(side: bool, B: Board) -> bool:
    '''
    checks if configuration of B is stalemate for side

    Hints: 
    - use is_check
    - use can_move_to 
    '''
    if is_check(side, B):
        return False

    S, pieces = B
    for p in pieces:
        if p.side == side:
            for x in range(1, S + 1):
                for y in range(1, S + 1):
                    if isinstance(p, Queen):
                        if p.can_move_to(x, y, B):
                            return False
                    elif isinstance(p, King):
                        if p.can_move_to(x, y, B):
                            return False
    return True


def read_board(filename: str) -> Board:
    '''
    reads board configuration from file in current directory in plain format
    raises IOError exception if file is not valid (see section Plain board configurations)
    '''
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f.readlines()]
    except Exception as ex:
        raise IOError(f"Cannot read file: {ex}")

    if len(lines) < 3:
        raise IOError("File must contain three lines: size, white pieces, black pieces")

    # Parse board size
    try:
        S = int(lines[0])
    except ValueError:
        raise IOError("First line must be an integer board size")
    if not (3 <= S <= 26):
        raise IOError("Board size must be between 3 and 26 inclusive")

    def parse_pieces(line: str, side: bool) -> List[Piece]:
        pieces: List[Piece] = []
        if line.strip() == "":
            return pieces
        tokens = [tok.strip() for tok in line.split(',')]
        for tok in tokens:
            if tok == "":
                continue
            if len(tok) < 2:
                raise IOError("Invalid piece token")
            kind = tok[0]
            loc = tok[1:]
            x, y = location2index(loc)
            if not (1 <= x <= S and 1 <= y <= S):
                raise IOError("Piece location out of bounds")
            if kind == 'K':
                pieces.append(King(x, y, side))
            elif kind == 'Q':
                pieces.append(Queen(x, y, side))
            else:
                raise IOError("Unknown piece kind; only K or Q are allowed")
        return pieces

    white_pieces = parse_pieces(lines[1], True)
    black_pieces = parse_pieces(lines[2], False)

    # Validate exactly one king per side
    if sum(isinstance(p, King) for p in white_pieces) != 1:
        raise IOError("There must be exactly one white king")
    if sum(isinstance(p, King) for p in black_pieces) != 1:
        raise IOError("There must be exactly one black king")

    # Validate no overlaps
    occupied: set[tuple[int, int]] = set()
    all_pieces: List[Piece] = []
    for p in white_pieces + black_pieces:
        pos = (p.pos_x, p.pos_y)
        if pos in occupied:
            raise IOError("Two pieces occupy the same square")
        occupied.add(pos)
        all_pieces.append(p)

    return (S, all_pieces)


def save_board(filename: str, B: Board) -> None:
    '''saves board configuration into file in current directory in plain format'''
    S, pieces = B

    white_tokens: List[str] = []
    black_tokens: List[str] = []

    for p in pieces:
        prefix = 'K' if isinstance(p, King) else 'Q'
        loc = index2location(p.pos_x, p.pos_y)
        tok = f"{prefix}{loc}"
        if p.side:
            white_tokens.append(tok)
        else:
            black_tokens.append(tok)

    # Stable ordering: sort for reproducibility
    white_tokens.sort()
    black_tokens.sort()

    content = [
        str(S),
        ", ".join(white_tokens),
        ", ".join(black_tokens),
    ]
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("\n".join(content))


def find_black_move(B: Board) -> tuple[Piece, int, int]:
    '''
    returns (P, x, y) where a Black piece P can move on B to coordinates x,y according to chess rules 
    assuming there is at least one black piece that can move somewhere

    Hints: 
    - use can_move_to
    - possibly, use methods of random library
    '''
    S, pieces = B
    black_pieces = [p for p in pieces if not p.side]
    random.shuffle(black_pieces)
    coords = [(x, y) for x in range(1, S + 1) for y in range(1, S + 1)]
    random.shuffle(coords)

    for p in black_pieces:
        for (x, y) in coords:
            if isinstance(p, Queen):
                if p.can_move_to(x, y, B):
                    return (p, x, y)
            elif isinstance(p, King):
                if p.can_move_to(x, y, B):
                    return (p, x, y)

    # As per assumption, should not reach here if there exists a move
    raise RuntimeError("No valid black moves found, although one was assumed to exist")


def conf2unicode(B: Board) -> str:
    '''converts board cofiguration B to unicode format string (see section Unicode board configurations)'''
    S, pieces = B
    # Map positions to unicode chars
    pos_to_char: dict[tuple[int, int], str] = {}
    for p in pieces:
        if p.side:
            # White
            ch = "\u2654" if isinstance(p, King) else "\u2655"
        else:
            # Black
            ch = "\u265A" if isinstance(p, King) else "\u265B"
        pos_to_char[(p.pos_x, p.pos_y)] = ch

    figure_space = "\u2001"
    lines: List[str] = []
    for y in range(S, 0, -1):
        line_chars: List[str] = []
        for x in range(1, S + 1):
            line_chars.append(pos_to_char.get((x, y), figure_space))
        lines.append("".join(line_chars))
    return "\n".join(lines)


_move_regex = re.compile(r"^([a-z])(\d{1,2})([a-z])(\d{1,2})$")


def _parse_move_str(move: str) -> tuple[str, int, str, int]:
    move = move.strip()
    m = _move_regex.match(move)
    if not m:
        raise ValueError("Invalid move format")
    col1, row1, col2, row2 = m.groups()
    x1, y1 = location2index(col1 + row1)
    x2, y2 = location2index(col2 + row2)
    return (col1 + row1, y1, col2 + row2, y2)  # return with y values, though not used externally


def _parse_move_to_coords(move: str) -> tuple[int, int, int, int]:
    move = move.strip()
    m = _move_regex.match(move)
    if not m:
        raise ValueError("Invalid move format")
    col1, row1, col2, row2 = m.groups()
    x1, y1 = location2index(col1 + row1)
    x2, y2 = location2index(col2 + row2)
    return x1, y1, x2, y2


def main() -> None:
    '''
    runs the play

    Hint: implementation of this could start as follows:
    filename = input("File name for initial configuration: ")
    ...
    '''
    while True:
        filename = input("File name for initial configuration: ")
        if filename.strip() == "QUIT":
            return
        try:
            B = read_board(filename.strip())
            break
        except IOError:
            print("This is not a valid file. File name for initial configuration: ", end="")

    print("The initial configuration is:")
    print(conf2unicode(B))

    while True:
        user = input("Next move of White: ").strip()
        if user == "QUIT":
            out_fn = input("File name to store the configuration: ")
            save_board(out_fn.strip(), B)
            print("The game configuration saved.")
            return

        # Parse and validate move
        try:
            x1, y1, x2, y2 = _parse_move_to_coords(user)
        except ValueError:
            print("This is not a valid move.", end=" ")
            continue

        S, _ = B
        if not (1 <= x1 <= S and 1 <= y1 <= S and 1 <= x2 <= S and 1 <= y2 <= S):
            print("This is not a valid move.", end=" ")
            continue

        if not is_piece_at(x1, y1, B):
            print("This is not a valid move.", end=" ")
            continue

        P = piece_at(x1, y1, B)
        if not P.side:
            print("This is not a valid move.", end=" ")
            continue

        can_move = False
        if isinstance(P, Queen):
            can_move = P.can_move_to(x2, y2, B)
        elif isinstance(P, King):
            can_move = P.can_move_to(x2, y2, B)
        else:
            can_move = False

        if not can_move:
            print("This is not a valid move.", end=" ")
            continue

        # Apply white move
        B = P.move_to(x2, y2, B)
        print("The configuration after White's move is:")
        print(conf2unicode(B))

        # Check for game end against Black
        if is_checkmate(False, B):
            print("Game over. White wins.")
            return
        if is_stalemate(False, B):
            print("Game over. Stalemate.")
            return

        # Black move
        P_black, bx, by = find_black_move(B)
        move_str = index2location(P_black.pos_x, P_black.pos_y) + index2location(bx, by)
        B = P_black.move_to(bx, by, B)
        print(f"Next move of Black is {move_str}. The configuration after Black's move is:")
        print(conf2unicode(B))

        # Check for game end against White
        if is_checkmate(True, B):
            print("Game over. Black wins.")
            return
        if is_stalemate(True, B):
            print("Game over. Stalemate.")
            return


if __name__ == '__main__':
    main()