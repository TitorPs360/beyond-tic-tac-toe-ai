## About Beyond Tic Tac Toe AI

_BeyondTicTacToeAI_ - a project for training an AI to play TicTacToe Game, but not traditional game, it's Beyond Tic Tac Toe Game by using reinforcement learning (Q-learning).

In this project, I made Traditional Tic Tac Toe game which can be controlled by click on game gui. Also I create Beyond Tic Tac Toe game that we can select the size to place the mark. And another important part is the use of reinforcement learning to create AI to play this game.

## Youtube

For more information can be seen in my [video](https://youtu.be/3q8Gh3yA9pw) on YouTube.

[![new_thumb](./fig/cover.png)]("https://youtu.be/3q8Gh3yA9pw")

## Requirements

- Anaconda with Python 3
- Git

## Install

```
git clone https://github.com/TitorPs360/beyond-tic-tac-toe-ai
cd beyond-tic-tac-toe-ai
conda create --name <env> --file requirements.txt
```

## Usage

1. Open CMD or Terminal

   ![alt text](./fig/step1.png?raw=true)

2. Activate anaconda environment

   ```
   conda activate <env>
   ```

3. How to play

- Basic Controller
  Key | Control
  --- | -------
  Left Click | Place Mark
  Q | Quiet Game
  R | Restart Game

- Run Game

  - For Traditional Tic Tac Toe

    - Script

    ```
    python traditional_game.py
    ```

    - Result

    |                    Start Game                    |                    Playing Game                    |
    | :----------------------------------------------: | :------------------------------------------------: |
    | ![Start Original](./fig/original01.png?raw=true) | ![Playing Original](./fig/original02.png?raw=true) |

  - For Beyond Tic Tac Toe (Human vs Human)

    - Script

    ```
    python beyond_game.py
    ```

    - Result

      |                   Start Game                   |                   Playing Game                   |
      | :--------------------------------------------: | :----------------------------------------------: |
      | ![Start Original](./fig/beyond01.png?raw=true) | ![Playing Original](./fig/beyond02.png?raw=true) |

  - For Training AI (AI vs AI)

    - Script

    ```
    python training.py
    ```

    - Result

    ![Training](./fig/training.png?raw=true)

  - For Beyond Tic Tac Toe (AI vs Human)

    - Script

    ```
    python play_with_ai.py
    ```

    - Result

    ![Play with AI](./fig/playwithai.png?raw=true)

4. Enjoy your Tic Tac Toe

## Training Result

![Training result](./fig/training_result.png?raw=true)
