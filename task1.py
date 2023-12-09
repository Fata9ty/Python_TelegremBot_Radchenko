
def draw_board(board):
    for i in range(3):
        print(' | '.join(board[i]))
        print('--------------')

'''
Задокументированная фукнция из шага № 2 задания № 1
def ask_and_make_move(player, board):
    x, y = input(f"{player}, введите координаты x и y (например, 0 0): ").strip().split()
    x, y = int(x), int(y)
    if (0 <= x <= 2) and (0 <= y <= 2) and (board[x][y] == '  '):
        board[x][y] = player
    else:
        print("Клетка занята. Попробуйте снова.")
        ask_and_make_move(player, board)
        '''

def ask_move(player, board):
    x, y = input(f'{player}, введите координаты x и y (например, 0 0): ').strip().split()
    x, y = int(x), int(y)
    if (0 <= x <= 2) and (0 <= y <= 2) and (board[x][y] == '   '):
        return x, y
    else:
        print('Клетка занята. Введите координаты еще раз.')
        return ask_move(player, board)
def make_move(player, board, x, y):
    if board[x][y] != '   ':
        print('Клетка занята.')
        return False
    board[x][y] = player
    return True

def ask_and_make_move(player, board):
    x, y = ask_move(player, board)
    make_move(player, board, x, y)

def check_win(player, board):
    for i in range(3):
        if board[i] == [player, player, player]:
            return True
        if board[0][i] == player and board[1][i] == player and board[2][i] == player:
            return True
    if board[0][0] == player and board[1][1] == player and board[2][2] == player:
        return True
    if board[0][2] == player and board[1][1] == player and board[2][0] == player:
        return True
    return False

def tic_tac_toe():
    while True:
        board = [['   ' for i in range(3)] for j in range(3)]
        player = ' X '
        while True:
            draw_board(board)
            ask_and_make_move(player, board)
            if check_win(player, board):
                print('%s Вы выйиграли!' % player)
                break
            draw = False
            for row in board:
                for cell in row:
                    if cell == '   ':
                        draw = True
            if not draw:
                break
            player = ' O ' if player == ' X ' else ' X '
            restart = input("Хотите сыграть еще раз? (y/n) ")
            if restart.lower() != "y":
                break

if __name__ == '__main__':
    new_game = tic_tac_toe()
    new_game
