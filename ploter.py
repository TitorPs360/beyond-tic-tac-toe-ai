import matplotlib.pyplot as plt
from IPython import display

plt.ion()


def plot(statistic, save=False):
    display.clear_output(wait=True)
    display.display(plt.gcf())
    plt.clf()
    plt.title('Learning how to play Tic Tac Toe')
    plt.xlabel('Number of Rounds')
    plt.ylabel('Games')

    plt.plot(statistic["round"], statistic["player1_win"], label="Player 1 win")
    plt.plot(statistic["round"], statistic["player2_win"], label="Player 2 win")
    plt.plot(statistic["round"], statistic["player2_win"], label="Player 2 win")
    plt.plot(statistic["round"], statistic["draw"], label="Draw")
    plt.plot(statistic["round"], statistic["player1_deckout"], label="Player 1 deckout")
    plt.plot(statistic["round"], statistic["player2_deckout"], label="Player 2 deckout")

    plt.ylim(ymin=0)

    plt.legend()
    # plt.text(len(scores)-1, scores[-1], str(scores[-1]))
    # plt.text(len(mean_scores)-1, mean_scores[-1], str(mean_scores[-1]))
    plt.show(block=False)

    if save:
        plt.savefig('result.png')
    # plt.pause(.1)
