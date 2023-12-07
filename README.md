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
- (DONE - Not needed, character assignment only happens after join) Listen to UpdatePlayers when waiting for nickname
- "YOU" marker in the lobby. Use parentheses next to player nickname (e.g. "Ms. Scarlet: Kevin (YOU)")
- Checkmark in lobby if player is ready. This may require server changes as well to broadcast ready.

### GameView
- Game Observation
  - When game starts, player view should change to observe game events even if it's not their turn
    - movement 
    - suggestions
    - accusation (correct/incorrect)
      - incorrect: show dialog and continue observation (add indicator for person who has lost) 
        - the waiting for turn text should instead default to accusing incorrectly
        - end turn and start next player's turn  
    - (DONE) Game indicator for whose turn it is

- Board
  - (DONE) lobby and YOU indicator
  - Show which cards are given to the player 
  - (optional) add secret passageway indicators
  - (optional) ability to draw weapon tokens

- Meeting QA
  - check on turn order + disprove order
  - limit number of connections to the server
  - 
QA: 
- Each player's cards are unique
- ![](QA.png)

