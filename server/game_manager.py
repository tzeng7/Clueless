from messages.messages import DealCards, YourTurn, BaseMessage, Suggest, Move, EndTurn, RequestDisprove, Disprove
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
        self.current_player = None
        self.players: list[ServerPlayer] = sorted(players, key=lambda x: x.player_id.character.value, reverse=True)
        self.board: Board = Board(players=[player.player_id for player in self.players])
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
        self.current_player = self.players[self.turn % len(self.players)]
        self.current_player.Send(YourTurn(turn_id=self.turn))

    def end_turn(self, end_action: EndTurn):
        self.SendToAll(end_action)
        self.next_turn()

    def move(self, player, move_action: Move):
        # TODO: Add error handling: throw when the move is invalid
        self.SendToAll(move_action)

    def suggest(self, suggest_action: Suggest):
        # move accused to accuser's location
        self.SendToAll(suggest_action)

        print("up to here")
        current = suggest_action.player_id
        index = 0
        for i in range(len(self.players)):
            if current.__eq__(self.players[i].player_id):
                index = i
        next_player = self.players[(index + 1) % len(self.players)]
        request_disprove = RequestDisprove(suggest_action)
        self.SendToPlayerWithId(next_player.player_id, request_disprove)
        #TODO: move weapon into location
        #TODO: move suggested character

    def disprove(self, disprove: Disprove):
        self.SendToPlayerWithId(disprove.suggest.player_id, disprove)
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

        cards.extend(
            [Card(CardType.CHARACTER, x.value) for x in Character if not x.value == self.winning_combination[0]])
        cards.extend([Card(CardType.LOCATION, x.value) for x in Location if not x.value == self.winning_combination[1]])
        cards.extend([Card(CardType.WEAPON, x.value) for x in Weapon if not x.value == self.winning_combination[2]])
        random.shuffle(cards)
        return cards

    ## disprove


    ################################
    #       NETWORKING HELPERS     #
    ################################

    def SendToPlayerWithId(self, player_id: PlayerID, data: BaseMessage):
        for player in self.players:
            if player_id == player.player_id:
                player.Send(data)

    def SendToAll(self, data: BaseMessage):
        [p.Send(data) for p in self.players]
