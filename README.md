# Clueless Setup
## Setting up Virtual Environment for Clueless using Poetry

### Download Poetry for Mac

"pip3 install poetry" / "brew install poetry" (if you use homebrew)

### Setting up the Virtual Environment Mac

- poetry config virtualenvs.in-project true

- poetry install

- go to interpreter settings: add local interpreter 

  - select poetry environment

### Download Poetry for Windows

- Follow https://www.jetbrains.com/help/pycharm/poetry.html for poetry installation.

- poetry config virtualenvs.in-project true

- poetry install

- go to interpreter settings: add local interpreter
  - select base interpreter (python 3.11)
  - poetry executable found in link above



# TODO List
## Game Client
### TitleView
- Listen to UpdatePlayers when waiting for nickname
- "YOU" marker in the lobby. This should be reusable since we can use the lobby in the GameView to show whose turn it is.
- (BUG) Image resizing for lobby avatar
- Checkmark in lobby if player is ready. This may require server changes as well to broadcast ready.
- Add Text: "Game starts when all players click READY!"

### GameView
- Game Observation
  - When game starts, player view should change to observe game events even if it's not their turn
    - movement
    - suggestions
    - (optional) disprove. This probably requires server changes
    - accusation (correct/incorrect)
      - correct: transition to game over view for all players
      - incorrect: show dialog and continue observation (add indicator for person who has lost)
    - end turn + next player
  - Game indicator for whose turn it is
- Board
  - (optional) add secret passageway indicators
  - ability to draw overlapping characters
  - (optional) ability to draw weapon tokens
- Action Box
  - ability to deselect or cancel
- Disprove
  - show menu dialog for which card was sent to suggester
