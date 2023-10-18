from model.board_enums import Location, Direction
from model.player import PlayerToken, PlayerID


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

    def move(self, player_id, position):
        player_token = self.player_tokens[player_id]
        if not self.grid[position[0]][position[1]].can_add():
            print("Error: Cannot add player to space") # TODO: Throw?
            return
        if player_token.position is None:
            self.grid[position[0]][position[1]].add(player_token)
        else:
            from_position = player_token.position
            self.grid[from_position[0]][from_position[1]].remove(player_token)
            self.grid[position[0]][position[1]].add(player_token)
        player_token.position = position

    def move_in_direction(self, player_id, direction):
        player_token = self.player_tokens[player_id]
        try:
            new_position = self.calculate_new_position(player_token.position, direction)
            self.move(player_id, new_position)
        except:
            print("Error: Cannot move in direction")

    def get_movement_options(self, player_id) -> list[(Direction, (int, int))]:
        player_token = self.player_tokens[player_id]
        valid_directions = []
        for direction in Direction:
            try:
                new_position = self.__calculate_new_position(player_token.position, direction)
                if self.grid[new_position[0]][new_position[1]].can_add():
                    valid_directions.append((direction, new_position))
            except ValueError:
                print(f"{direction.value} is not valid")
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
