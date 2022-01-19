import pygame, sys
import numpy as np

# init pygame
pygame.init()

# define game dimension
WIDTH = 600
HEIGHT = 1000

TABLE_WIDTH = 600
TABLE_HEIGHT = 600

LINE_WIDTH = 15
WIN_LINE_WIDTH = 15
BOARD_ROWS = 3
BOARD_COLS = 3
SQUARE_SIZE = 200
DECK_SIZE = 120

CIRCLE_RADIUS = {
  5 : 60,
  4 : 50,
  3 : 40,
  2 : 30,
  1 : 20
}

CIRCLE_WIDTH = {
  5 : 15,
  4 : 13,
  3 : 11,
  2 : 9,
  1 : 7
}

CROSS_WIDTH = 25

SPACE = 55

# define game color
RED = (255, 0, 0)
BG_COLOR = (20, 200, 160)
LINE_COLOR = (23, 145, 135)
CIRCLE_COLOR = (239, 231, 200)
CROSS_COLOR = (66, 66, 66)

class TicTacToeGame:
  def __init__(self):
    # setup display
    self.screen = pygame.display.set_mode( (WIDTH, HEIGHT) )
    pygame.display.set_caption( 'TIC TAC TOE' )

    # set background
    self.screen.fill( BG_COLOR )

    # draw frame for tic tac toe
    self.draw_frame()

    # store center coordinates
    self.center_x_list = []

    # draw deck
    self.draw_deck()

    # setup game array
    self.board = np.zeros( (BOARD_ROWS, BOARD_COLS) )

    # setup game over state
    self.game_over = False

    # setup turn
    self.player = 1

    # show starting text
    print("Starting game")

  # draw frame for tic tac toe
  def draw_frame(self):
    # horizontal line
    pygame.draw.line( self.screen, LINE_COLOR, (0, SQUARE_SIZE), (WIDTH, SQUARE_SIZE), LINE_WIDTH )
    pygame.draw.line( self.screen, LINE_COLOR, (0, 2 * SQUARE_SIZE), (WIDTH, 2 * SQUARE_SIZE), LINE_WIDTH )
    pygame.draw.line( self.screen, LINE_COLOR, (0, 3 * SQUARE_SIZE), (WIDTH, 3 * SQUARE_SIZE), LINE_WIDTH )
    pygame.draw.line( self.screen, LINE_COLOR, (0, 4 * SQUARE_SIZE), (WIDTH, 4 * SQUARE_SIZE), LINE_WIDTH )

    # vertical line
    pygame.draw.line( self.screen, LINE_COLOR, (SQUARE_SIZE, SQUARE_SIZE), (SQUARE_SIZE, HEIGHT - SQUARE_SIZE), LINE_WIDTH )
    pygame.draw.line( self.screen, LINE_COLOR, (2 * SQUARE_SIZE, SQUARE_SIZE), (2 * SQUARE_SIZE, HEIGHT - SQUARE_SIZE), LINE_WIDTH )

  def draw_deck(self):
    for i in range(1,6):
      start_position_x = 0
      for j in range(1, i):
        # blank for other mark
        start_position_x += CIRCLE_RADIUS[j] * 3

      # add offset
      start_position_x += CIRCLE_RADIUS[i] * 1.5

      self.center_x_list.append(start_position_x)

      pygame.draw.circle( self.screen, CIRCLE_COLOR, (int( start_position_x ), int( 4 * SQUARE_SIZE + SQUARE_SIZE//2 )), CIRCLE_RADIUS[i], CIRCLE_WIDTH[i] )
    # for i in range(1,6):
    #   pygame.draw.circle( self.screen, CIRCLE_COLOR, (int( ( i - 1 ) * DECK_SIZE + DECK_SIZE//2 ), int( 4 * SQUARE_SIZE + SQUARE_SIZE//2 )), CIRCLE_RADIUS[i], CIRCLE_WIDTH[i] )
  
  # draw X or O in table
  def draw_mark(self):
    for row in range(BOARD_ROWS):
      for col in range(BOARD_COLS):
        # drawing O
        if self.board[row][col] == 1:
          pygame.draw.circle( self.screen, CIRCLE_COLOR, (int( col * SQUARE_SIZE + SQUARE_SIZE//2 ), int( (row + 1) * SQUARE_SIZE + SQUARE_SIZE//2 )), CIRCLE_RADIUS[1], CIRCLE_WIDTH[1] )
        # drawing X
        elif self.board[row][col] == 2:
          pygame.draw.line( self.screen, CROSS_COLOR, (col * SQUARE_SIZE + SPACE, (row + 1) * SQUARE_SIZE + SQUARE_SIZE - SPACE), (col * SQUARE_SIZE + SQUARE_SIZE - SPACE, (row + 1) * SQUARE_SIZE + SPACE), CROSS_WIDTH )	
          pygame.draw.line( self.screen, CROSS_COLOR, (col * SQUARE_SIZE + SPACE, (row + 1) * SQUARE_SIZE + SPACE), (col * SQUARE_SIZE + SQUARE_SIZE - SPACE, (row + 1) * SQUARE_SIZE + SQUARE_SIZE - SPACE), CROSS_WIDTH )
        # blank

  # store player mark in array
  def place_mark(self, row, col):
    self.board[row][col] = self.player

  # check this block is available? 
  def check_available(self, row, col):
    return self.board[row][col] == 0

  # check board is full -> draw
  def is_board_full(self):
    for row in range(BOARD_ROWS):
      for col in range(BOARD_COLS):
        if self.board[row][col] == 0:
          return False
    return True

  # check win
  def check_win(self):
    # win in colum
    for col in range(BOARD_COLS):
      if self.board[0][col] == self.player and self.board[1][col] == self.player and self.board[2][col] == self.player:
        self.draw_vertical_winning_line(col)
        return True

    # win in row
    for row in range(BOARD_ROWS):
      if self.board[row][0] == self.player and self.board[row][1] == self.player and self.board[row][2] == self.player:
        self.draw_horizontal_winning_line(row)
        return True

    # win asc diagonal
    if self.board[2][0] == self.player and self.board[1][1] == self.player and self.board[0][2] == self.player:
      self.draw_asc_diagonal()
      return True

    # win desc diagonal
    if self.board[0][0] == self.player and self.board[1][1] == self.player and self.board[2][2] == self.player:
      self.draw_desc_diagonal()
      return True

    return False

  # draw vertical win line
  def draw_vertical_winning_line(self, col):
    posX = col * SQUARE_SIZE + SQUARE_SIZE//2

    if self.player == 1:
      color = CIRCLE_COLOR
    elif self.player == 2:
      color = CROSS_COLOR

    pygame.draw.line( self.screen, color, (posX, SQUARE_SIZE + 15), (posX, HEIGHT - SQUARE_SIZE - 15 ), LINE_WIDTH )

  # draw horizontal win line
  def draw_horizontal_winning_line(self, row):
    posY = ( row + 1 ) * SQUARE_SIZE + SQUARE_SIZE//2

    if self.player == 1:
      color = CIRCLE_COLOR
    elif self.player == 2:
      color = CROSS_COLOR

    pygame.draw.line( self.screen, color, (15, posY), (WIDTH - 15, posY), WIN_LINE_WIDTH )

  # draw asc diagonal win line
  def draw_asc_diagonal(self):
    if self.player == 1:
      color = CIRCLE_COLOR
    elif self.player == 2:
      color = CROSS_COLOR

    pygame.draw.line( self.screen, color, (15, HEIGHT - SQUARE_SIZE - 15), (WIDTH - 15, SQUARE_SIZE + 15), WIN_LINE_WIDTH )

  # draw desc diagonal win line
  def draw_desc_diagonal(self):
    if self.player == 1:
      color = CIRCLE_COLOR
    elif self.player == 2:
      color = CROSS_COLOR

    pygame.draw.line( self.screen, color, (15, SQUARE_SIZE + 15), (WIDTH - 15, HEIGHT - SQUARE_SIZE - 15), WIN_LINE_WIDTH )

  # restart game
  def restart(self):
    # fill background
    self.screen.fill( BG_COLOR )
    # draw table
    self.draw_frame()

    # set all board to 0
    self.board = np.zeros( (BOARD_ROWS, BOARD_COLS) )

  # play step
  def play(self):
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        sys.exit()

      # get mark position
      if event.type == pygame.MOUSEBUTTONDOWN and not self.game_over:

        mouseX = event.pos[0] 
        mouseY = event.pos[1] 

        # mouse position to row,col
        clicked_row = int(mouseY // SQUARE_SIZE)
        # clicked_col = int(mouseX // SQUARE_SIZE)

        # opponent side click
        if (clicked_row == 0):
          print('Opponent side')
        # our side click
        elif (clicked_row == 4):
          for i in range(0, 5):
            if self.center_x_list[i] - int( CIRCLE_RADIUS[ i + 1 ] // 2 ) - int( CIRCLE_WIDTH[ i + 1 ] // 2 ) < mouseX and mouseX < self.center_x_list[i] + int( CIRCLE_RADIUS[ i + 1 ] // 2 ) + int( CIRCLE_WIDTH[ i + 1 ] // 2 ):
              print(i)
              break
        # click in table
        else:
          clicked_col = int(mouseX // SQUARE_SIZE)

          # check markable
          if self.check_available( clicked_row - 1, clicked_col ):
            
            # place mark
            self.place_mark( clicked_row - 1, clicked_col )

            # check win
            if self.check_win():
              print(f"Player {'O' if self.player == 1 else 'X'} win")
              self.game_over = True

            # check draw
            if self.is_board_full():
              print("draw")
              self.game_over = True

            # draw mark
            self.draw_mark()

            # switch side
            self.player = self.player % 2 + 1

      if event.type == pygame.KEYDOWN:
        # restart game
        if event.key == pygame.K_r:
          print("Restarting game")
          self.restart()
          self.player = 1
          self.game_over = False
        # quiet game
        if event.key == pygame.K_q:
          print("Quiet game")
          pygame.quit()
          quit()

    pygame.display.update()

    return self.game_over

if __name__ == '__main__':
  game = TicTacToeGame()

  while True:
    gameover = game.play()
