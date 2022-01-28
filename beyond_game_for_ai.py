import pygame, sys
import numpy as np
import random
import torch
from collections import deque
from os import path
from model import Linear_QNet, QTrainer
import ploter

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

# game speed
SPEED = 500

# Machine learning constant
MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.001

DEVICE = 'cuda'

# AI player class
class Player:
  def __init__(self, name, exp_rate=0.3):
    # define player name
    self.name = name

    # record all states taken
    self.states = [] 

    # learning rate
    self.lr = 0.2

    # balance exploration and exploitation -> discover new thing
    self.exp_rate = exp_rate

    # gamma
    self.decay_gamma = 0.9

    # store data
    self.memory = deque(maxlen=MAX_MEMORY)

    # convert state to value
    self.states_value = {}

    # check model already exists
    if path.exists('model_' + str(self.name) + '.pth'):
      self.model = Linear_QNet(28, 45)

      file_name = 'model_' + str(self.name) + '.pth'
      model_folder_path = './model'
      file_name = path.join(model_folder_path, file_name)

      self.model.load_state_dict(torch.load(file_name))
      self.model.eval()

      self.model = self.model.to(DEVICE)
      print('Loaded last model: ', file_name)
    else:
      self.model = Linear_QNet(28, 45)
      self.model = self.model.to(DEVICE)

    # define trainer
    self.trainer = QTrainer(self.model, lr=LR, gamma=self.decay_gamma)

  # convert table and deck in to 1 line string
  def getState(self, board, deck, symbol):
    state = []

    for i in range(3):
      for j in range(3):
        if str(board[i][j][0]) == symbol:
          state.append(1)
        elif str(board[i][j][0]) == symbol % 2 + 1:
          state.append(-1)
        else:
          state.append(0)
        
        state.append(int(board[i][j][1]))

    for d in deck[symbol]:
      state.append(d)

    for d in deck[symbol % 2 + 1]:
      state.append(d)

    return np.array(state, dtype=int)

  # remember state
  def remember(self, state, action, reward, next_state, done):
    self.memory.append((state, action, reward, next_state, done))

  # train to long memory
  def train_long_memory(self):
    if len(self.memory) > BATCH_SIZE:
        mini_sample = random.sample(self.memory, BATCH_SIZE)  # list of tuples
    else:
        mini_sample = self.memory

    states, actions, rewards, next_states, dones = zip(*mini_sample)
    self.trainer.train_step(states, actions, rewards, next_states, dones)

  # add short memory
  def train_short_memory(self, state, action, reward, next_state, done):
    self.trainer.train_step(state, action, reward, next_state, done)

  # thinking the action to do
  def chooseAction(self, current_board, avaible_size, symbol, state):
    available_positions = {}

    # finding available position and size
    for i in range(3):
      for j in range(3):
        if current_board[i][j][0] != symbol:
          avaible_size_list = []
          for k in avaible_size:
            if k > current_board[i][j][1]:
              avaible_size_list.append(k)

          if len(avaible_size_list) > 0:
            available_positions[3*i + j] = avaible_size_list

    # choose between prediction and discover new thing
    if np.random.uniform(0, 1) <= self.exp_rate:
      # take random action
      random_position = random.choice(list(available_positions.keys()))
      random_size = available_positions[random_position]
      random_size_index = np.random.choice(len(random_size))

      raw_best_choice = (random_size[random_size_index] - 1) * 9 + random_position

      action = [random_position, random_size[random_size_index], raw_best_choice]
    else:
      state0 = torch.tensor(state, dtype=torch.float).to('cuda')
      prediction = self.model(state0)
      best_choice = torch.argmax(prediction).to('cuda').item()

      size = best_choice // 9
      position = best_choice % 9 

      action = [position, size + 1, best_choice]
    
    return action

  # save trained model
  def saveModel(self):
    file_name = 'model_' + str(self.name) + '.pth'
    model_folder_path = './model'
    file_name = path.join(model_folder_path, file_name)
    torch.save(self.model.state_dict(), file_name)

  # load trained model
  def loadModel(self, filename):
    self.model = Linear_QNet(28, 45)

    self.model.load_state_dict(torch.load(filename))
    self.model.eval()

    self.model = self.model.to(DEVICE)
    print('Loaded last model: ', filename)

# Human player class
class HumanPlayer:
  def __init__(self, name):
    # define player name
    self.name = name

# Game class
class TicTacToeGameAI:
  def __init__(self, player1, player2):
    # setup display
    self.screen = pygame.display.set_mode( (WIDTH, HEIGHT) )
    pygame.display.set_caption( 'TIC TAC TOE' )

    # set background
    self.screen.fill( BG_COLOR )

    # draw frame for tic tac toe
    self.draw_frame()

    # pygame clock
    self.clock = pygame.time.Clock()

    # store center coordinates
    self.center_x_list = []

    # define player
    self.player1 = player1
    self.player2 = player2

    # statistic
    self.player1_win = 0
    self.player2_win = 0
    self.player1_deckout = 0
    self.player2_deckout = 0
    self.draw = 0

    self.statistic = {
      "round": [],
      "player1_win": [],
      "player2_win": [],
      "draw": [],
      "player1_deckout": [],
      "player2_deckout": [],
    }

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

  # draw deck in game
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
    if self.check_available(row, col):
      self.board[row][col][0] = self.player
      self.board[row][col][1] = self.selecting_size
      self.deck[self.player][self.selecting_size - 1] = 0
      return True
    return False

  # check this block is available? 
  def check_available(self, row, col):
    return self.board[row][col][0] != self.player and self.board[row][col][1] < self.selecting_size and self.deck[self.player][self.selecting_size - 1] == 1

  # get avaible size in deck
  def get_available_size(self):
    avaible_size = []
    for i in range(5):
      if self.deck[self.player][i] == 1:
        avaible_size.append(i + 1)

    return avaible_size

  # check board is full -> draw
  def is_board_full(self):
    for row in range(BOARD_ROWS):
      for col in range(BOARD_COLS):
        if self.board[row][col][0] == 0:
          return False
    return True

  # check deck is out
  def is_deck_empty(self):
    return self.deck[self.player] == [0, 0, 0, 0, 0]

  # get board hash
  def getState(self):
    state = []

    for i in range(3):
      for j in range(3):
        if str(self.board[i][j][0]) == self.player:
          state.append(1)
        elif str(self.board[i][j][0]) == self.player % 2 + 1:
          state.append(-1)
        else:
          state.append(0)

        state.append(int(self.board[i][j][1]))

    for d in self.deck[self.player]:
      state.append(d)

    for d in self.deck[self.player % 2 + 1]:
      state.append(d)

    return np.array(state, dtype=int)

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

    # available size for players
    self.deck = {
      1 : [1, 1, 1, 1, 1],
      2 : [1, 1, 1, 1, 1]
    }

    # draw deck
    self.draw_deck()

    # set all board to 0
    self.board = np.zeros( (BOARD_ROWS, BOARD_COLS, 2) )

    # setup turn 1 for O
    self.player = 1

    # setup game over state
    self.game_over = False

    # selecting size
    self.selecting_size = 0

  # play step for ai vs ai
  def train(self, rounds=100):
    for i in range(rounds):
      pygame.event.pump()

      print(f"Round {i}")

      # plot status
      ploter.plot(self.statistic)

      # add statistic
      self.statistic["round"].append(i)
      self.statistic["player1_win"].append(self.player1_win)
      self.statistic["player2_win"].append(self.player2_win)
      self.statistic["draw"].append(self.draw)
      self.statistic["player1_deckout"].append(self.player1_deckout)
      self.statistic["player2_deckout"].append(self.player2_deckout)

      while not self.game_over:
        # get state
        state_old = self.getState()

        # check player 1 out of deck
        if self.is_deck_empty():
          print("Player 1 Out of deck")
          self.player1_deckout += 1

          # train short memory
          self.player1.train_short_memory(state_old, player1_action[2], -1, state_new, True)
          self.player2.train_short_memory(state_old, player2_action[2], 2, state_new, True)

          # remember
          self.player1.remember(state_old, player1_action[2], -1, state_new, True)
          self.player2.remember(state_old, player2_action[2], 2, state_new, True)

          self.game_over = True

        # place mark when avialable
        while True:
          # player 1 turn
          player1_action = self.player1.chooseAction(self.board, self.get_available_size(), self.player, state_old)

          self.selecting_size = player1_action[1]

          mark_row = player1_action[0] // 3
          mark_col = player1_action[0] % 3

          if self.place_mark( mark_row, mark_col ):
            break

        # draw mark
        self.draw_mark()

        # get new state after place mark
        state_new = self.getState()

        # check player 1 win
        if self.check_win():
          print("Player 1 (O) win")
          self.player1_win += 1

          # train short memory
          self.player1.train_short_memory(state_old, player1_action[2], 2, state_new, True)
          self.player2.train_short_memory(state_old, player2_action[2], -1, state_new, True)

          # remember
          self.player1.remember(state_old, player1_action[2], 2, state_new, True)
          self.player2.remember(state_old, player2_action[2], -1, state_new, True)

          self.game_over = True
        # draw
        elif self.is_board_full():
          print("Draw")
          self.draw += 1

          # train short memory
          self.player1.train_short_memory(state_old, player1_action[2], 0, state_new, True)
          self.player2.train_short_memory(state_old, player2_action[2], 0, state_new, True)

          # remember
          self.player1.remember(state_old, player1_action[2], 0, state_new, True)
          self.player2.remember(state_old, player2_action[2], 0, state_new, True)

          self.game_over = True
        else:
          # train short memory
          self.player1.train_short_memory(state_old, player1_action[2], 1, state_new, False)

          # remember
          self.player1.remember(state_old, player1_action[2], 1, state_new, False)

          # get state
          state_old = self.getState()

          # Player 2 turn
          self.player = self.player % 2 + 1

          # check player 2 out of deck
          if self.is_deck_empty():
            print("Player 2 Out of deck, Player 1 win")
            self.player2_deckout += 1

            # train short memory
            self.player1.train_short_memory(state_old, player1_action[2], 2, state_new, True)
            self.player2.train_short_memory(state_old, player2_action[2], -1, state_new, True)

            # remember
            self.player1.remember(state_old, player1_action[2], 2, state_new, True)
            self.player2.remember(state_old, player2_action[2], -1, state_new, True)

            self.game_over = True

          # place mark when avialable
          while True:
            player2_action = self.player2.chooseAction(self.board, self.get_available_size(), self.player, state_old)

            self.selecting_size = player2_action[1]

            mark_row = player2_action[0] // 3
            mark_col = player2_action[0] % 3

            if self.place_mark( mark_row, mark_col ):
              break

          # draw mark
          self.draw_mark()

          # get new state after place mark
          state_new = self.getState()

          # check win
          if self.check_win():
            print("Player 2 (X) win")
            self.player2_win += 1

            # train short memory
            self.player1.train_short_memory(state_old, player1_action[2], -1, state_new, True)
            self.player2.train_short_memory(state_old, player2_action[2], 2, state_new, True)

            # remember
            self.player1.remember(state_old, player1_action[2], -1, state_new, True)
            self.player2.remember(state_old, player2_action[2], 2, state_new, True)
          
            self.game_over = True
          # draw
          elif self.is_board_full() or self.is_deck_empty():
            print("Draw")
            self.draw += 1

            # train short memory
            self.player1.train_short_memory(state_old, player1_action[2], 0, state_new, True)
            self.player2.train_short_memory(state_old, player2_action[2], 0, state_new, True)

            # remember
            self.player1.remember(state_old, player1_action[2], 0, state_new, True)
            self.player2.remember(state_old, player2_action[2], 0, state_new, True)

            self.game_over = True

          # train short memory
          self.player2.train_short_memory(state_old, player2_action[2], 1, state_new, False)

          # remember
          self.player2.remember(state_old, player2_action[2], 1, state_new, False)

          # switch to player 1 turn
          self.player = self.player % 2 + 1
        
        self.reset_screen()
        self.selecting_size = 0

        # update screen
        pygame.display.update()
        self.clock.tick(SPEED)
      
      # restart game after game end
      self.restart()

    print(f"Player 1 win : {self.player1_win}, Player 2 win : {self.player2_win}, Draw : {self.draw}")
    self.player1.saveModel()
    self.player2.saveModel()

    # save latest result
    ploter.plot(self.statistic, True)

  def play(self):
    while not self.game_over:
      # player 1 turn
      print('AI turn')

      # get state
      state_old = self.getState()

      # place mark
      while True:
        # player 1 turn
        player1_action = self.player1.chooseAction(self.board, self.get_available_size(), self.player, state_old)

        self.selecting_size = player1_action[1]

        mark_row = player1_action[0] // 3
        mark_col = player1_action[0] % 3

        if self.place_mark( mark_row, mark_col ):
          break

      # draw mark
      self.draw_mark()

      # check win
      if self.check_win():
        print("Player 1 (O) win")
        self.player1_win += 1
        self.game_over = True
        print("AI will conquer the world")
        pygame.display.update()
      # draw
      elif self.is_board_full() or self.is_deck_empty():
        print("Draw")
        self.draw += 1
        self.game_over = True
      else:
        # Player 2 turn
        print('Human turn')

        self.player = self.player % 2 + 1

        self.reset_screen()
        pygame.display.update()

        player2_done = False

        while not player2_done:
          pygame.display.update()

          for event in pygame.event.get():
            if event.type == pygame.QUIT:
              sys.exit()

            # get mark position
            if event.type == pygame.MOUSEBUTTONDOWN and not self.game_over:

              mouseX = event.pos[0] 
              mouseY = event.pos[1] 

              # mouse position to row,col
              clicked_row = int(mouseY // SQUARE_SIZE)

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
                    print("Player 2 (X) win")
                    self.player2_win += 1
                    self.game_over = True
                  # check draw
                  elif self.is_board_full() or self.is_deck_empty():
                    print("draw")
                    self.draw += 1
                    self.game_over = True
                  else:
                    # switch side
                    self.player = self.player % 2 + 1

                    # reset screen
                    self.reset_screen()

                    # reset size
                    self.selecting_size = 0

                    # player 2 is done
                    player2_done = True

            if event.type == pygame.KEYDOWN:
              # restart game
              if event.key == pygame.K_r:
                print("Restarting game")
                self.restart()
                player2_done = True
              # quiet game
              if event.key == pygame.K_q:
                print("Quiet game")
                self.player1.saveModel()
                pygame.quit()
                quit()
      
      self.selecting_size = 0
  
      pygame.display.update()

    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        sys.exit()

      if event.type == pygame.KEYDOWN:
        # restart game
        if event.key == pygame.K_r:
          print("Restarting game")
          self.restart()
        # quiet game
        if event.key == pygame.K_q:
          print("Quiet game")
          self.player1.saveModel()
          pygame.quit()
          quit()
    
