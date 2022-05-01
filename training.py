from beyond_game_for_ai import *

if __name__ == '__main__':
  # training AI vs AI
  player1 = Player("player1", exp_rate=0.3)
  player2 = Player("player2", exp_rate=0.5)

  Game = TicTacToeGameAI(player1, player2)

  print("Training AI vs AI")
  Game.train(100000)
