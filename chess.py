import tkinter as tk
from tkinter import messagebox

root = tk.Tk()
root.resizable(width=False, height=False)
size = 75
root.title('chess')
canvas = tk.Canvas(root, width=size * 8 + 250, height=size * 8, bg='white')

WHITE = 1
BLACK = 2
figure_list = [['♖', '♘', '♗', '♕', "♔", '♗', '♘', '♖'],
               ['♙'] * 8, [''] * 8, [''] * 8, [''] * 8, [''] * 8, ['♟'] * 8,
               ['♜', '♞', '♝', '♛', "♚", '♝', '♞', '♜']]


def draw_field():
    for i in range(8):
        for j in range(8):
            color = 'white' if (i + j) % 2 != 0 else 'green'
            x1, y1, x2, y2 = j * size, i * size, j * size + size, i * size + size
            canvas.create_rectangle((x1, y1), (x2, y2), fill=color)
            canvas.create_text((x1 + x2) // 2, (y1 + y2) // 2, text=figure_list[i][j], font="Verdana 45")
            root.update()


draw_field()


def opponent(color):
    if color == WHITE:
        return BLACK
    return WHITE


def correct_coords(row, col):
    return 0 <= row < 8 and 0 <= col < 8


def check_move(row, col, row1, col1, color):
    if not correct_coords(row1, col1):
        return False
    if row == row1 and col == col1:
        return False
    piece1 = field[row1][col1]
    if piece1 is not None:
        if piece1.get_color() == color:
            return False
    return True


def bishop(row, col, row1, col1):
    if row - col == row1 - col1:
        step = 1 if (row1 >= row) else -1
        for r in range(row + step, row1, step):
            c = col - row + r
            if not (board.get_piece(r, c) is None):
                return False
        return True
    if row + col == row1 + col1:
        step = 1 if (row1 >= row) else -1
        for r in range(row + step, row1, step):
            c = row + col - r
            if not (board.get_piece(r, c) is None):
                return False
        return True


def rook(row, col, row1, col1):
    if row != row1 and col != col1:
        return False

    step = 1 if (row1 >= row) else -1
    for r in range(row + step, row1, step):
        if not (board.get_piece(r, col) is None):
            return False

    step = 1 if (col1 >= col) else -1
    for c in range(col + step, col1, step):
        if not (board.get_piece(row, c) is None):
            return False
    return True


class Figure:
    def __init__(self, color, name):
        self.color = color
        self.name = name
        self.sc = "w" if self.color == WHITE else 'b'

    def get_color(self):
        return self.color

    def char(self):
        return self.name[0] if self.name != 'Knight' else "N"

    def can_attack(self, board, row, col, row1, col1):
        return self.can_move(board, row, col, row1, col1)

    def can_move(self, board, row, col, row1, col1):
        pass

    def __repr__(self):
        return self.sc + self.name[0] if self.name != 'Knight' else self.sc + 'N'


class Rook(Figure):

    def __init__(self, color):
        super().__init__(color, 'Rook')
        self.count_move = 0

    def can_move(self, board, row, col, row1, col1):
        return rook(row, col, row1, col1)


class Pawn(Figure):

    def __init__(self, color):
        super().__init__(color, 'Pawn')

    def can_move(self, board, row, col, row1, col1):
        if col != col1:
            return False

        if self.color == WHITE:
            direction = 1
            start_row = 1
        else:
            direction = -1
            start_row = 6

        if row + direction == row1:
            return True

        if (row == start_row
                and row + 2 * direction == row1
                and field[row + direction][col] is None):
            return True
        return False

    def can_attack(self, board, row, col, row1, col1):
        direction = 1 if (self.color == WHITE) else -1
        return (row + direction == row1
                and (col + 1 == col1 or col - 1 == col1))


class Knight(Figure):
    def __init__(self, color):
        super().__init__(color, 'Knight')

    def can_move(self, board, row, col, row1, col1):
        if abs(row - row1) * abs(col - col1) == 2:
            return True
        return False


class King(Figure):
    def __init__(self, color):
        super().__init__(color, 'King')
        self.moved = 0

    def can_move(self, board, row, col, row1, col1):
        if abs(row - row1) <= 1 and abs(col - col1) <= 1 and check_move(row, col, row1, col1, self.color):
            return True
        ind = 7 if self.color == BLACK else 0
        if self.moved != 0:
            return False
        if isinstance(field[ind][4], King) and col1 == 2:
            if isinstance(field[ind][0], Rook) and field[ind][0].count_move == 0:
                cor = 0
                for i in range(1, 4):
                    if field[ind][i] is None:
                        cor += 1
                if cor == 3:
                    field[ind][2], field[ind][3] = King(self.color), Rook(self.color)
                    field[ind][4], field[ind][0] = None, None
                    self.moved = 1
                    field[ind][3].count_move = 1
                    figure_list[ind][3] = figure_list[ind][0]
                    figure_list[ind][0] = ''
                    return True
        if isinstance(field[ind][4], King) and col1 == 6:
            if isinstance(field[ind][7], Rook) and field[ind][7].count_move == 0:
                cor = 0
                for i in range(5, 7):
                    if field[ind][i] is None:
                        cor += 1
                if cor != 2:
                    return False
                field[ind][6], field[ind][5] = King(self.color), Rook(self.color)
                field[ind][4], field[ind][7] = None, None
                self.moved = 1
                field[ind][5].count_move = 1
                figure_list[ind][5] = figure_list[ind][7]
                figure_list[ind][7] = ''
                return True
        return False


class Queen(Figure):
    def __init__(self, color):
        super().__init__(color, 'Queen')

    def can_move(self, board, row, col, row1, col1):
        if not check_move(row, col, row1, col1, self.color):
            return False
        if rook(row, col, row1, col1) or bishop(row, col, row1, col1):
            return True
        return False


class Bishop(Figure):
    def __init__(self, color):
        super().__init__(color, 'Bishop')

    def can_move(self, board, row, col, row1, col1):
        return bishop(row, col, row1, col1)


field = []
for row in range(8):
    field.append([None] * 8)
field[0] = [Rook(WHITE), Knight(WHITE), Bishop(WHITE), Queen(WHITE), King(WHITE), Bishop(WHITE), Knight(WHITE),
            Rook(WHITE)]
field[1] = [Pawn(WHITE)] * 8
field[6] = [Pawn(BLACK)] * 8
field[7] = [Rook(BLACK), Knight(BLACK), Bishop(BLACK), Queen(BLACK), King(BLACK), Bishop(BLACK), Knight(BLACK),
            Rook(BLACK)]


class Board:
    def __init__(self):
        self.color = WHITE

    def get_piece(self, row, col):
        if correct_coords(row, col):
            return field[row][col]
        return None

    def move_piece(self, row, col, row1, col1):
        if not check_move(row, col, row1, col1, self.color):
            return False
        piece = field[row][col]
        if piece is None:
            return False
        if piece.get_color() != self.color:
            return False
        if field[row1][col1] is not None and field[row1][col1].get_color() == piece.get_color():
            return False
        if field[row1][col1] is None:
            if not piece.can_move(self, row, col, row1, col1):
                return False
        elif field[row1][col1].get_color() == opponent(piece.get_color()):
            if not piece.can_attack(self, row, col, row1, col1):
                return False

        field[row][col] = None
        field[row1][col1] = piece
        self.color = opponent(self.color)
        figure_list[row1][col1] = figure_list[row][col]
        figure_list[row][col] = ''
        return True


coord = []
board = Board()


def add_to_all(event):
    global coord
    x = (canvas.winfo_pointery() - canvas.winfo_rooty()) // size
    y = (canvas.winfo_pointerx() - canvas.winfo_rootx()) // size
    coord.extend((x, y))
    if len(coord) == 4:
        if board.move_piece(coord[0], coord[1], coord[2], coord[3]):
            draw_field()
        coord = []


def new_game():
    global figure_list, field, coord
    figure_list = [['♖', '♘', '♗', '♕', "♔", '♗', '♘', '♖'], ['♙'] * 8,
                   [''] * 8, [''] * 8, [''] * 8, [''] * 8,
                   ['♟'] * 8, ['♜', '♞', '♝', '♛', "♚", '♝', '♞', '♜']]
    coord = []
    field = []
    for _ in range(8):
        field.append([None] * 8)
    field[0] = [Rook(WHITE), Knight(WHITE), Bishop(WHITE), Queen(WHITE), King(WHITE), Bishop(WHITE), Knight(WHITE),
                Rook(WHITE)]
    field[1] = [Pawn(WHITE)] * 8
    field[6] = [Pawn(BLACK)] * 8
    field[7] = [Rook(BLACK), Knight(BLACK), Bishop(BLACK), Queen(BLACK), King(BLACK), Bishop(BLACK), Knight(BLACK),
                Rook(BLACK)]
    board.color = WHITE
    draw_field()


def closed():
    if tk.messagebox.askokcancel('Выход из игры', "Хотите выйти?"):
        root.destroy()


root.protocol("WM_DELETE_WINDOW", closed)
b0 = tk.Button(root, text='Новая игра', command=new_game)
b0.place(x=(size * 8 + 30), y=30)
canvas.bind_all("<Button-1>", add_to_all)
canvas.pack()
root.mainloop()
