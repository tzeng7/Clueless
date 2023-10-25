from model.board_enums import Location, Direction, Character
from model.player import PlayerToken, PlayerID
from typing import cast


# abstract class with capacity
class Space:
    def __init__(self, capacity):
        self.capacity = capacity
        self.players: dict[PlayerID: PlayerToken] = []

    def can_add(self):
        return len(self.players) < self.capacity

    def add(self, player):
        self.players.append(player)

    def remove(self, player):
        self.players.remove(player)


class Room(Space):
    def __init__(self, room_type: Location):
        super().__init__(6)
        self.room_type = room_type


class Hallway(Space):
    def __init__(self):
        super().__init__(1)


class Void(Space):
    def __init__(self):
        super().__init__(0)


class Board:
    def __init__(self, players: list[PlayerID]):
        self.player_tokens: dict[PlayerID, PlayerToken] = dict(
            [(player, PlayerToken(player_id=player)) for player in players]
        )
        self.grid = [
            [Room(Location.STUDY), Hallway(), Room(Location.HALL), Hallway(), Room(Location.LOUNGE)],
            [Hallway(), Void(), Hallway(), Void(), Hallway()],
            [Room(Location.LIBRARY), Hallway(), Room(Location.BILLIARD), Hallway(), Room(Location.DINING)],
            [Hallway(), Void(), Hallway(), Void(), Hallway()],
            [Room(Location.CONSERVATORY), Hallway(), Room(Location.BALLROOM), Hallway(), Room(Location.KITCHEN)]
        ]
        for player in self.player_tokens:
            starting_position = player.character.get_starting_position()
            self.grid[starting_position[0]][starting_position[1]].add(self.player_tokens[player])
            self.player_tokens[player].position = starting_position


    # def to_string(self):
    #     for x in range(len(self.grid)):
    #         for y in range(len(self.grid[0])):
    #             print(f"Position: {(x,y)} has "),
    #             print( for player in self.grid[x][y].players)

    def move(self, player_id, position):
        player_token = self.player_tokens[player_id]
        if not self.grid[position[0]][position[1]].can_add():
            print("Error: Cannot add player to space")
            return
        if player_token.position is None:
            self.grid[position[0]][position[1]].add(player_token)
        else:
            from_position = player_token.position
            self.grid[from_position[0]][from_position[1]].remove(player_token)
            self.grid[position[0]][position[1]].add(player_token)
        player_token.position = position

    def get_movement_options(self, player_id) -> list[(Direction, (int, int))]:
        player_token = self.player_tokens[player_id]
        # if not player_token.position:
        #     return [(Direction.INITIALIZE, player_id.character.get_starting_position())]
        valid_directions = []
        # for direction in [d for d in Direction if d.value > Direction.INITIALIZE.value]:
        for direction in Direction:
            try:
                new_position = self.__calculate_new_position(player_token.position, direction)
                if self.grid[new_position[0]][new_position[1]].can_add():
                    valid_directions.append((direction, new_position))
            except ValueError:
                print(f"Excluding {direction.name}") #what's going on here
        return valid_directions

    def __calculate_new_position(self, from_position, direction):
        new_position = from_position
        match direction:
            case Direction.UP if from_position[0] > 0:
                new_position = (from_position[0] - 1, from_position[1])

            case Direction.DOWN if from_position[0] < 4:
                new_position = (from_position[0] + 1, from_position[1])
            case Direction.LEFT if from_position[1] > 0:
                new_position = (from_position[0], from_position[1] - 1)
            case Direction.RIGHT if from_position[1] < 4:
                new_position = (from_position[0], from_position[1] + 1)
            case Direction.SECRET_PASSAGEWAY if from_position == (0, 0) or from_position == (4, 4):
                new_position = (4 - from_position[0], 4 - from_position[1])
            case Direction.SECRET_PASSAGEWAY if from_position == (0, 4) or from_position == (4, 0):
                new_position = (from_position[1], from_position[0])
            case _:
                raise ValueError("Invalid direction")
        return new_position

    def get_player_space(self, player_id) -> Space:
        position = self.player_tokens[player_id].position
        return self.grid[position[0]][position[1]]

    def is_in_room(self, player_id):
        space = self.get_player_space(player_id)
        return isinstance(space, Room)

    def get_player_id(self, character: Character):
        for player in self.player_tokens:
            if player.character == character:
                return player

    def get_player_position(self, player_id):
        return self.player_tokens[player_id].position

    def __str__(self):
        description = []
        description.append("""
                                0   1   2   3   4
                              ┌───┐   ┌───┐   ┌───┐
                            0 │STU├───┤HAL├───┤LOU│
                              └─┬─┘   └─┬─┘   └─┬─┘
                            1   │       │       │
                              ┌─┴─┐   ┌─┴─┐   ┌─┴─┐
                            2 │LIB├───┤BIL├───┤DIN│
                              └─┬─┘   └─┬─┘   └─┬─┘
                            3   │       │       │
                              ┌─┴─┐   ┌─┴─┐   ┌─┴─┐
                            4 │CON├───┤BAL├───┤KIT│
                              └───┘   └───┘   └───┘
                            """)
        for player in sorted(self.player_tokens.values(), key=lambda x: x.player_id.character.ordinal_value):
            if not player.position:
                description.append(f"{player.character} not initialized.")
            elif self.is_in_room(player.player_id):
                description.append(f"{player.character} is in {cast(Room, self.get_player_space(player.player_id)).room_type}")
            else:
                player_position = player.position
                if player_position[0] % 2 == 0:
                    first_room = self.grid[player_position[0]][player_position[1]-1].room_type
                    second_room = self.grid[player_position[0]][player_position[1]+1].room_type
                else:
                    first_room = self.grid[player_position[0]-1][player_position[1]].room_type
                    second_room = self.grid[player_position[0]+1][player_position[1]].room_type
                description.append(f"{player.character} is in the hallway between {first_room} and {second_room}.")

        return "\n".join(description)

