import pygame, sys
import numpy as np
import pickle

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

CROSS_SIZE = {
  5 : 120,
  4 : 100,
  3 : 80,
  2 : 60,
  1 : 40
}

CROSS_WIDTH = {
  5 : 25,
  4 : 23,
  3 : 21,
  2 : 19,
  1 : 17
}

# define game color
RED = (255, 0, 0)
BG_COLOR = (20, 200, 160)
LINE_COLOR = (23, 145, 135)
CIRCLE_COLOR = (239, 231, 200)
CROSS_COLOR = (66, 66, 66)
SELECTING_COLOR = (237, 191, 33)

class Player:
  def __init__(self, name, exp_rate=0.3):
    self.name = name
    self.states = []  # record all states taken
    self.lr = 0.2
    self.exp_rate = exp_rate
    self.decay_gamma = 0.9
    self.states_value = {}  # state -> value

  def getHash(self, board):
    boardHash = ''

    for i in range(3):
      for j in range(3):
        boardHash += board[i][j][0]
        boardHash += board[i][j][1]

    return boardHash

  def chooseAction(self, current_board, avaible_size, symbol):
    available_positions = {}

    for i in range(3):
      for j in range(3):
        if current_board[i][j][0] != symbol:
          avaible_size_list = []
          for k in avaible_size:
            if k > current_board[i][j][1]:
              avaible_size_list.append[k]

          if len(avaible_size_list) > 0:
            available_positions[i + j] = avaible_size_list

    if np.random.uniform(0, 1) <= self.exp_rate:
      # take random action
      random_position = np.random.choice(len(available_positions))
      random_size = available_positions[random_position]
    else:
      value_max = -999
      for p in available_positions:
        next_board = current_board.copy()
        next_board[p] = symbol
        next_boardHash = self.getHash(next_board)
        value = 0 if self.states_value.get(next_boardHash) is None else self.states_value.get(next_boardHash)
        # print("value", value)
        if value >= value_max:
            value_max = value
            action = p
    # print("{} takes action {}".format(self.name, action))
    return action

  # append a hash state
  def addState(self, state):
    self.states.append(state)

  # at the end of game, backpropagate and update states value
  def feedReward(self, reward):
    for st in reversed(self.states):
      if self.states_value.get(st) is None:
        self.states_value[st] = 0
      self.states_value[st] += self.lr * (self.decay_gamma * reward - self.states_value[st])
      reward = self.states_value[st]

  def reset(self):
    self.states = []

  def savePolicy(self):
    fw = open('policy_' + str(self.name), 'wb')
    pickle.dump(self.states_value, fw)
    fw.close()

  def loadPolicy(self, file):
    fr = open(file, 'rb')
    self.states_value = pickle.load(fr)
    fr.close()


class HumanPlayer:
    def __init__(self, name):
        self.name = name

    def chooseAction(self, positions):
        while True:
            row = int(input("Input your action row:"))
            col = int(input("Input your action col:"))
            action = (row, col)
            if action in positions:
                return action

    # append a hash state
    def addState(self, state):
        pass

    # at the end of game, backpropagate and update states value
    def feedReward(self, reward):
        pass

    def reset(self):
        pass
class TicTacToeGameAI:
  def __init__(self, player1, player2):
    # setup display
    self.screen = pygame.display.set_mode( (WIDTH, HEIGHT) )
    pygame.display.set_caption( 'TIC TAC TOE' )

    # set background
    self.screen.fill( BG_COLOR )

    # draw frame for tic tac toe
    self.draw_frame()

    # store center coordinates
    self.center_x_list = []

    # setup turn 1 for O
    self.player = 1

    # available size for players
    self.deck = {
      1 : [1, 1, 1, 1, 1],
      2 : [1, 1, 1, 1, 1]
    }

    # draw deck
    self.draw_deck()

    # setup game array
    self.board = np.zeros( (BOARD_ROWS, BOARD_COLS, 2) )

    # setup game over state
    self.game_over = False

    # selecting size
    self.selecting_size = 0

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
    if self.player == 1:
      x_row = 0
      o_row = 4
    elif self.player == 2:
      x_row = 4
      o_row = 0

    for i in range(1,6):
      start_position_x = 0
      for j in range(1, i):
        # blank for other mark
        start_position_x += CIRCLE_RADIUS[j] * 3

      # add offset
      start_position_x += CIRCLE_RADIUS[i] * 1.5

      self.center_x_list.append(start_position_x)

      # draw O
      if self.deck[1][i - 1] == 1:
        pygame.draw.circle( self.screen, CIRCLE_COLOR, (int( start_position_x ), int( o_row * SQUARE_SIZE + SQUARE_SIZE//2 )), CIRCLE_RADIUS[i], CIRCLE_WIDTH[i] )

      # draw X
      if self.deck[2][i - 1] == 1:
        pygame.draw.line( self.screen, CROSS_COLOR, (start_position_x - CROSS_SIZE[i] // 2, x_row * SQUARE_SIZE + SQUARE_SIZE // 2 - CROSS_SIZE[i] // 2), (start_position_x + CROSS_SIZE[i] // 2, x_row * SQUARE_SIZE + SQUARE_SIZE // 2 + CROSS_SIZE[i] // 2 ), CROSS_WIDTH[i] )
        pygame.draw.line( self.screen, CROSS_COLOR, (start_position_x - CROSS_SIZE[i] // 2, x_row * SQUARE_SIZE + SQUARE_SIZE // 2 + CROSS_SIZE[i] // 2), (start_position_x + CROSS_SIZE[i] // 2, x_row * SQUARE_SIZE + SQUARE_SIZE // 2 - CROSS_SIZE[i] // 2 ), CROSS_WIDTH[i] )
  
  # draw selecting symbol on selecting size
  def draw_selecting_size(self, size):
    pygame.draw.circle( self.screen, SELECTING_COLOR, (int( self.center_x_list[size] ), int( 5 * SQUARE_SIZE - 15 )), 10 )

  # draw X or O in table
  def draw_mark(self):
    for row in range(BOARD_ROWS):
      for col in range(BOARD_COLS):
        # drawing O
        if self.board[row][col][0] == 1:
          pygame.draw.circle( self.screen, CIRCLE_COLOR, (int( col * SQUARE_SIZE + SQUARE_SIZE//2 ), int( (row + 1) * SQUARE_SIZE + SQUARE_SIZE//2 )), CIRCLE_RADIUS[self.board[row][col][1]], CIRCLE_WIDTH[self.board[row][col][1]] )
        # drawing X
        elif self.board[row][col][0] == 2:
          pygame.draw.line( self.screen, CROSS_COLOR, ((col + 0.5) * SQUARE_SIZE - CROSS_SIZE[self.board[row][col][1]] // 2, (row + 1) * SQUARE_SIZE + SQUARE_SIZE // 2 - CROSS_SIZE[self.board[row][col][1]] // 2), ((col + 0.5) * SQUARE_SIZE + CROSS_SIZE[self.board[row][col][1]] // 2, (row + 1) * SQUARE_SIZE + SQUARE_SIZE // 2 + CROSS_SIZE[self.board[row][col][1]] // 2 ), CROSS_WIDTH[self.board[row][col][1]] )
          pygame.draw.line( self.screen, CROSS_COLOR, ((col + 0.5) * SQUARE_SIZE - CROSS_SIZE[self.board[row][col][1]] // 2, (row + 1) * SQUARE_SIZE + SQUARE_SIZE // 2 + CROSS_SIZE[self.board[row][col][1]] // 2), ((col + 0.5) * SQUARE_SIZE + CROSS_SIZE[self.board[row][col][1]] // 2, (row + 1) * SQUARE_SIZE + SQUARE_SIZE // 2 - CROSS_SIZE[self.board[row][col][1]] // 2 ), CROSS_WIDTH[self.board[row][col][1]] )
        # blank

  # redraw the screen
  def reset_screen(self):
      # set background
    self.screen.fill( BG_COLOR )

    # draw frame for tic tac toe
    self.draw_frame()

    # draw X O on table
    self.draw_mark()

    # draw deck
    self.draw_deck()

  # store player mark in array
  def place_mark(self, row, col):
    self.board[row][col][0] = self.player
    self.board[row][col][1] = self.selecting_size
    self.deck[self.player][self.selecting_size - 1] = 0

  # check this block is available? 
  def check_available(self, row, col):
    return self.board[row][col][0] != self.player and self.board[row][col][1] < self.selecting_size

  # check board is full -> draw
  def is_board_full(self):
    for row in range(BOARD_ROWS):
      for col in range(BOARD_COLS):
        if self.board[row][col][0] == 0:
          return False
    return True

  # check deck is out
  def is_deck_empty(self):
    return self.deck[1] == [0, 0, 0, 0, 0] and self.deck[2] == [0, 0, 0, 0, 0]

  # check win
  def check_win(self):
    # win in colum
    for col in range(BOARD_COLS):
      if self.board[0][col][0] == self.player and self.board[1][col][0] == self.player and self.board[2][col][0] == self.player:
        self.draw_vertical_winning_line(col)
        return True

    # win in row
    for row in range(BOARD_ROWS):
      if self.board[row][0][0] == self.player and self.board[row][1][0] == self.player and self.board[row][2][0] == self.player:
        self.draw_horizontal_winning_line(row)
        return True

    # win asc diagonal
    if self.board[2][0][0] == self.player and self.board[1][1][0] == self.player and self.board[0][2][0] == self.player:
      self.draw_asc_diagonal()
      return True

    # win desc diagonal
    if self.board[0][0][0] == self.player and self.board[1][1][0] == self.player and self.board[2][2][0] == self.player:
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

    # draw deck
    self.draw_deck()

    # set all board to 0
    self.board = np.zeros( (BOARD_ROWS, BOARD_COLS, 2) )

    # setup turn 1 for O
    self.player = 1

    # available size for players
    self.deck = {
      1 : [1, 1, 1, 1, 1],
      2 : [1, 1, 1, 1, 1]
    }

    # setup game over state
    self.game_over = False

    # selecting size
    self.selecting_size = 0

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
              # set selecting size
              self.selecting_size = i + 1
              
              # check size is available
              if self.deck[self.player][self.selecting_size - 1] == 1:
                # reset screen
                self.reset_screen()

                # draw size indicator
                self.draw_selecting_size(i)

                break
              else:
                print("This size is used")

                break
        # click in table
        else:
          clicked_col = int(mouseX // SQUARE_SIZE)

          # check markable
          if self.check_available( clicked_row - 1, clicked_col ):
            
            # place mark
            self.place_mark( clicked_row - 1, clicked_col )

            # draw mark
            self.draw_mark()

            # check win
            if self.check_win():
              print(f"Player {'O' if self.player == 1 else 'X'} win")
              self.game_over = True
            # check draw
            elif self.is_board_full():
              print("draw")
              self.game_over = True
            elif self.is_deck_empty():
              print("draw")
              self.game_over = True
            else:
              # switch side
              self.player = self.player % 2 + 1

              # reset screen
              self.reset_screen()

              # reset size
              self.selecting_size = 0

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
  game = TicTacToeGameAI()

  while True:
    gameover = game.play()
