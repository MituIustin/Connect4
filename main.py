import numpy as np
import random
import pygame
import sys
import math

# game variables

rows = 6            # number of rows
cols = 7            # number of cols
player = 0          # to determine the turn
ai = 1              # to determine the turn
player_piece = 1    # if a cells contains 1, that means player owns it
ai_piece = 2        # if a cells contains 2, that means ai owns it

win_len = 4
game_over = False

pygame.init()

cell_size = 100

width = cols * cell_size            # window width
height = (rows+1) * cell_size       # window height
size = (width, height)
depth = 5

rad = int(cell_size/2 - 5)          # radius

window = pygame.display.set_mode(size)
pygame.display.update()

myfont = pygame.font.SysFont("Aerial", 75)
turn = random.randint(player, ai)

# visual variables
colors = {}

def create_colors():
    colors["white"] = (255, 255, 255)
    colors["red"] = (252, 91, 122)
    colors["blue"] = (78, 193, 255)
    colors["green"] = (0, 255, 0)
    colors["black"] = (12, 12, 12)
    return colors
create_colors()


# Creates a matrix full of 0's

def create_board():
	board = np.zeros((rows,cols))
	return board

# Basically add a piece at top to a col

def drop_piece(board, row, col, piece):
	board[row][col] = piece

# Checks if a position is empty

def is_valid_location(board, col):
	return board[rows-1][col] == 0

# Returns the most top empty cell

def get_next_open_row(board, col):
	for r in range(rows):
		if board[r][col] == 0:
			return r

# Cheks if the game ended

def winning_move(board, piece):
	# Horizontal
 
	for c in range(cols-3):
		for r in range(rows):
			if board[r][c] == piece and board[r][c+1] == piece and board[r][c+2] == piece and board[r][c+3] == piece:
				return True

	# Vertical
	for c in range(cols):
		for r in range(rows-3):
			if board[r][c] == piece and board[r+1][c] == piece and board[r+2][c] == piece and board[r+3][c] == piece:
				return True

	# Down Right
	for c in range(cols-3):
		for r in range(rows-3):
			if board[r][c] == piece and board[r+1][c+1] == piece and board[r+2][c+2] == piece and board[r+3][c+3] == piece:
				return True

	# Up Right
	for c in range(cols-3):
		for r in range(3, rows):
			if board[r][c] == piece and board[r-1][c+1] == piece and board[r-2][c+2] == piece and board[r-3][c+3] == piece:
				return True

def evaluate_window(window, piece):
	score = 0
	enemy = player_piece
	if piece == player_piece:
		enemy = ai_piece

	if window.count(piece) == 4:
		score += 100000
	elif window.count(piece) == 3 and window.count(0) == 1:
		score += 5
	elif window.count(piece) == 2 and window.count(0) == 2:
		score += 2
	if window.count(enemy) == 3 and window.count(0) == 1:
		score -= 4

	return score

def score_position(board, piece):
	score = 0

	# Horizontal
 
	for r in range(rows):
		row_array = [int(i) for i in list(board[r,:])]
		for c in range(cols-3):
			window = row_array[c:c+win_len]
			score += evaluate_window(window, piece)

	# Vertical
 
	for c in range(cols):
		col_array = [int(i) for i in list(board[:,c])]
		for r in range(rows-3):
			window = col_array[r:r+win_len]
			score += evaluate_window(window, piece)

	# First Diagonal
 
	for r in range(rows-3):
		for c in range(cols-3):
			window = [board[r+i][c+i] for i in range(win_len)]
			score += evaluate_window(window, piece)

    # Second Diagonal

	for r in range(rows-3):
		for c in range(cols-3):
			window = [board[r+3-i][c+i] for i in range(win_len)]
			score += evaluate_window(window, piece)

	return score

# Checks if it's a winning position / draw position

def is_terminal_node(board):
	return winning_move(board, player_piece) or winning_move(board, ai_piece) or len(get_valid_locations(board)) == 0

# MIN MAX ALG

def minmax(board, depth, alpha, beta, maximizingPlayer):
	valid_locations = get_valid_locations(board)
	is_terminal = is_terminal_node(board)
	if depth == 0 or is_terminal:
		if is_terminal:
			if winning_move(board, ai_piece):
				return (None, 9999)
			elif winning_move(board, player_piece):
				return (None, -9999)
			else: # Game is over, no more valid moves
				return (None, 0)
		else: # Depth is zero
			return (None, score_position(board, ai_piece))
		
	if maximizingPlayer:
		value = -99999
		column = -1
		for col in valid_locations:
			row = get_next_open_row(board, col)
			b_copy = board.copy()
			drop_piece(b_copy, row, col, ai_piece)
			new_score = minmax(b_copy, depth-1, alpha, beta, False)[1]
			if new_score > value:
				value = new_score
				column = col
			alpha = max(alpha, value)
			if alpha >= beta:
				break
		return column, value

	else: 
		value = 99999
		column = -1
		for col in valid_locations:
			row = get_next_open_row(board, col)
			b_copy = board.copy()
			drop_piece(b_copy, row, col, player_piece)
			new_score = minmax(b_copy, depth-1, alpha, beta, True)[1]
			if new_score < value:
				value = new_score
				column = col
			beta = min(beta, value)
			if alpha >= beta:
				break
		return column, value

# Returns a list of all valid positions

def get_valid_locations(board):
	valid_locations = []
	for col in range(cols):
		if is_valid_location(board, col):
			valid_locations.append(col)
	return valid_locations

def draw_board(board):
    # Grid

	for c in range(cols):
		for r in range(rows):
			pygame.draw.rect(window, colors["blue"], (c*cell_size, r*cell_size+cell_size, cell_size, cell_size))
			pygame.draw.circle(window, colors["black"], (int(c*cell_size+cell_size/2), int(r*cell_size+cell_size+cell_size/2)), rad)
	
    # Circles

	for c in range(cols):
		for r in range(rows):		
			if board[r][c] == player_piece:
				pygame.draw.circle(window, colors["red"], (int(c*cell_size+cell_size/2), height-int(r*cell_size+cell_size/2)), rad)
			elif board[r][c] == ai_piece: 
				pygame.draw.circle(window, colors["green"], (int(c*cell_size+cell_size/2), height-int(r*cell_size+cell_size/2)), rad)
	pygame.display.update()
board = create_board()


texts = ["Easy", "Medium", "Hard"]
text_rects = []
for i, text in enumerate(texts):
    text_render = myfont.render(text, True, colors["black"])
    text_rect = text_render.get_rect(center=(width // 2, (i+1) * height // 4))
    text_rects.append(text_rect)
	
texts1 = ["A Star", "Min Max", "Retele Bayesiene"]
text_rects1 = []
for i, text in enumerate(texts1):
    text_render = myfont.render(text, True, colors["black"])
    text_rect = text_render.get_rect(center=(width // 2, (i+1) * height // 4))
    text_rects1.append(text_rect)

difficulty = None
algo  = None

def display_text(p):
    window.fill(colors["white"])
    if p == 1:
      for i, text in enumerate(texts):
        window.blit(myfont.render(text, True, colors["black"]), text_rects[i])
    else:
      for i, text in enumerate(texts1): 
        window.blit(myfont.render(text, True, colors["black"]), text_rects1[i])


while not game_over:
	for event in pygame.event.get():
		if difficulty == None:
			if event.type == pygame.MOUSEBUTTONDOWN:
				for i, rect in enumerate(text_rects):
					if rect.collidepoint(event.pos):
						difficulty = texts[i]
						print(difficulty)
						if i == 0:
							depth = 1
						elif i == 1:
							depth = 3
						else:
							depth = 5
						print(depth)
						window.fill(colors["black"])
						draw_board(board)
			display_text(1)
			pygame.display.flip()
		elif algo == None:
			if event.type == pygame.MOUSEBUTTONDOWN:
				for i, rect in enumerate(text_rects1):
					if rect.collidepoint(event.pos):
						algo = texts1[i]
						print(algo)
						window.fill(colors["black"])
						draw_board(board)
			display_text(2)
			pygame.display.flip()
		else:
			draw_board(board)
			if event.type == pygame.QUIT:
				sys.exit()

			if event.type == pygame.MOUSEBUTTONDOWN:
                # Player turn 

				if turn == player:
					posx = event.pos[0]
                    
          # Determine col

					col = int(math.floor(posx/cell_size))

					if is_valid_location(board, col):
						row = get_next_open_row(board, col)
						drop_piece(board, row, col, player_piece)

						if winning_move(board, player_piece):
							label = myfont.render("Player 1 wins!!", 1, colors["red"])
							window.blit(label, (40,10))
							game_over = True

						if turn == 1:
							turn = 0
						else:
							turn = 1  
						draw_board(board)
						print(board)
					else:
						print("You cant place the piece here!")
        # ai turn
		if turn == ai and not game_over:				
    
			col, minmax_score = minmax(board, 5, -9999, 9999, True)

			if is_valid_location(board, col):
                
				row = get_next_open_row(board, col)
				drop_piece(board, row, col, ai_piece)

				if winning_move(board, ai_piece):
					win_text = myfont.render("Player 2 wins!!", 1, colors["green"])
					window.blit(win_text, (40,10))
					game_over = True
                    
				draw_board(board)
				print(board)
				turn += 1
				turn = turn % 2

		if game_over:
			pygame.time.wait(1000)
