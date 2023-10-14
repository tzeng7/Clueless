from model.board_enums import Location, Direction
from model.player import PlayerToken, PlayerID


# abstract class with capacity
class Space:
    def __init__(self, capacity):
        self.capacity = capacity
        self.players: [PlayerToken] = []

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
    def __init__(self):
        self.player_tokens: dict[PlayerID, PlayerToken] = {}
        self.grid = [
            [Room(Location.STUDY), Hallway(), Room(Location.HALL), Hallway(), Room(Location.LOUNGE)],
            [Hallway(), Void(), Hallway(), Void(), Hallway()],
            [Room(Location.LIBRARY), Hallway(), Room(Location.BILLIARD), Hallway(), Room(Location.DINING)],
            [Hallway(), Void(), Hallway(), Void(), Hallway()],
            [Room(Location.CONSERVATORY), Hallway(), Room(Location.BALLROOM), Hallway(), Room(Location.KITCHEN)]
        ]

    def add_player(self, id: PlayerID):
        self.player_tokens[id] = PlayerToken()

    def initialize(self, player):
        player.position = player.character.get_starting_position()
        self.grid[player.position[0]][player.position[1]].add(player)

    def move(self, player, position):
        if not self.grid[position[0]][position[1]].can_add():
            print("Error: Cannot add player to space")
            return
        from_position = player.position
        self.grid[from_position[0]][from_position[1]].remove(player)
        self.grid[position[0]][position[1]].add(player)
        player.set_position(position)

    def move_in_direction(self, player, direction):
        try:
            new_position = self.__calculate_new_position(player.position, direction)
            self.move(player, new_position)
        except:
            print("Error: Cannot move in direction")

    def get_movement_options(self, player):
        valid_directions = []
        for direction in Direction:
            try:
                self.__calculate_new_position(player.position, direction)
                valid_directions.append(direction)
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
