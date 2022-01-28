from beyond_game_for_ai import *

if __name__ == '__main__':
  # training AI vs AI
  player1 = Player("player1", exp_rate=0.3)
  player2 = HumanPlayer("player2")

  player1.loadModel('./model/model_player1.pth')

  Game = TicTacToeGameAI(player1, player2)

  print("AI vs Human")

  while True:
    Game.play()