from messages.messages import DealCards, StartTurn, ClientAction, BaseMessage
from model.board import Board
from model.board_enums import Character, Location, Weapon, CardType
import random

from model.card import Card
from model.player import PlayerID
from server_player import ServerPlayer


# future features:
#   - lobby phase
#       - broadcasting users who have joined
#       - dropping from a lobby
#       - selecting your character
class GameManager:

    def __init__(self, players: [ServerPlayer]):
        # Play order = by Character Enum order, which is also the order the players joined the lobby
        self.players: list[ServerPlayer] = sorted(players, key=lambda x: x.player_id.character.value, reverse=True)
        self.board = Board()
        self.turn = -1
        self.winning_combination = None

    def start_game(self):
        # Distribute Cards
        cards = self.__create_cards()
        for i in range(0, len(cards)):
            self.players[i % len(self.players)].cards.append(cards[i])
        for player in self.players:
            player.Send(DealCards(cards=player.cards))
        self.next_turn()

    def next_turn(self):
        self.turn += 1
        next_player = self.players[self.turn % len(self.players)]
        next_player.Send(StartTurn(turn_id=self.turn))

    def end_turn(self, end_action: ClientAction.EndTurn):
        self.SendToAll(end_action)
        self.next_turn()

    def move(self, player, move_action: ClientAction.Move):
        # TODO: Needs implementation!
        # self.board.move(player, move_action.position)
        # TODO: Add error handling
        self.SendToAll(move_action)

    def suggest(self, accuser, accused, weapon):
        #move accused to accuser's location
        self.board.move(accused, accuser.position) #TODO: move weapon into location

        #cue suggestion_responses

    def accuse(self, accuser, character, weapon, location):
        # deactivate player if wrong; return boolean whether right or wrong
        if (character, weapon, location) == self.winning_combination:
            return 'Game Over'
        accuser.active = False
        return accuser + 'inactive'

    def __create_cards(self):
        cards = []

        # choose specific combination and distribute the rest
        self.winning_combination = (Card(CardType.CHARACTER, random.choice(list(Character))),
                                    Card(CardType.LOCATION, random.choice(list(Location))),
                                    Card(CardType.WEAPON, random.choice(list(Weapon))))

        cards.extend([Card(CardType.CHARACTER, x.value) for x in Character if not x.value == self.winning_combination[0]])
        cards.extend([Card(CardType.LOCATION, x.value) for x in Location if not x.value == self.winning_combination[1]])
        cards.extend([Card(CardType.WEAPON, x.value) for x in Weapon if not x.value == self.winning_combination[2]])
        random.shuffle(cards)
        return cards

    ################################
    #       NETWORKING HELPERS     #
    ################################

    def SendToPlayerWithId(self, player_id: PlayerID, data: BaseMessage):
        for player in self.players:
            if player_id == player.player_id:
                player.Send(data)

    def SendToAll(self, data: BaseMessage):
        [p.Send(data) for p in self.players]
