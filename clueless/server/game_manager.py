from clueless.messages.messages import DealCards, YourTurn, BaseMessage, Suggest, Move, EndTurn, RequestDisprove, Accuse, \
    Disprove, EndGame
from clueless.model.board import Board
from clueless.model.board_enums import Character, Location, Weapon, CardType
import random

from clueless.model.card import Card
from clueless.model.player import PlayerID
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
        self.players: list[ServerPlayer] = sorted(players, key=lambda x: x.player_id.character.ordinal_value)
        unassigned_characters = list(Character)[len(self.players):]  # we mint PlayerIDs in order of join right now

        dummy_players: list[PlayerID] = [PlayerID(nickname=character.name, character=character) for character in \
                                         unassigned_characters]
        self.board: Board = Board(players=[player.player_id for player in self.players] + dummy_players)
        self.turn = -1
        self.winning_combination = None

    def start_game(self):
        # Distribute Cards
        cards = self.__create_cards()
        print(self.winning_combination)
        for i in range(0, len(cards)):
            self.players[i % len(self.players)].cards.append(cards[i])
        for player in self.players:
            player.Send(DealCards(cards=player.cards))
        self.next_turn()

    def next_turn(self):
        self.turn += 1
        self.current_player = self.players[self.turn % len(self.players)]
        if self.current_player.active:
            self.current_player.Send(YourTurn(turn_id=self.turn))
        else:
            self.next_turn()

    def end_turn(self, end_action: EndTurn):
        self.SendToAll(end_action)
        self.next_turn()

    def move(self, player, move_action: Move):
        # TODO: Add error handling: throw when the move is invalid
        self.SendToAll(move_action)

    def find_index_player(self, player_id):
        index = 0
        for i in range(len(self.players)):
            if player_id.__eq__(self.players[i].player_id):
                index = i
        return index

    def suggest(self, suggest_action: Suggest):
        # move accused to accuser's location
        self.SendToAll(suggest_action)

        print("up to here")
        index = self.find_index_player(suggest_action.player_id)
        next_player = self.players[(index + 1) % len(self.players)]
        request_disprove = RequestDisprove(suggest_action)
        self.SendToPlayerWithId(next_player.player_id, request_disprove)
        # TODO: move weapon into location
        # TODO: move suggested character

    def disprove(self, disprove: Disprove):
        if not disprove.card:
            disproving_player = disprove.player_id
            index = self.find_index_player(disproving_player)
            next_player = self.players[(index + 1) % len(self.players)]
            if next_player.player_id == disprove.suggest.player_id:
                print("No players could disprove.")
                self.SendToPlayerWithId(disprove.suggest.player_id, Disprove(disprove.suggest.player_id,
                                                                             None,
                                                                             disprove.suggest))
            else:
                request_disprove = RequestDisprove(disprove.suggest)
                self.SendToPlayerWithId(next_player.player_id, request_disprove)
        else:
            self.SendToPlayerWithId(disprove.suggest.player_id, disprove)

    def accuse(self, accuser, accuse_action: Accuse):
        character, weapon, location = accuse_action.accusation
        if (character.value, location.value, weapon.value) == (self.winning_combination[0].card_value, self.winning_combination[1].card_value, self.winning_combination[2].card_value):
            game_over_message = f"Game Over! {accuser.player_id.nickname} made the correct accusation."
            accuse_action.is_correct = True
            self.SendToPlayerWithId(accuser.player_id,accuse_action)
            self.SendToAll(EndGame())
            print(game_over_message)
        else:
            accuser.active = False
            self.SendToPlayerWithId(accuser.player_id, accuse_action)
            print(f"{accuser.player_id.nickname} is inactive")

        #self.SendToAll(f"{accuser.player_id.nickname} is inactive")

    def __create_cards(self):
        cards = []

        # choose specific combination and distribute the rest

        self.winning_combination = (Card(CardType.CHARACTER, random.choice(list(Character)).value),
                                    Card(CardType.LOCATION, random.choice(list(Location)).value),
                                    Card(CardType.WEAPON, random.choice(list(Weapon)).value))
        cards.extend(
            [Card(CardType.CHARACTER, x.value)
             for x in Character if not x.value == self.winning_combination[0].card_value])
        cards.extend([Card(CardType.LOCATION, x.value)
                      for x in Location if not x.value == self.winning_combination[1].card_value])
        cards.extend([Card(CardType.WEAPON, x.value)
                      for x in Weapon if not x.value == self.winning_combination[2].card_value])
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
