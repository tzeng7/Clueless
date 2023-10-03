from board_enums import RoomType, Direction


# abstract class with capacity
class Space:
    def __init__(self, capacity):
        self.capacity = capacity
        self.players = []

    def can_add(self):
        return len(self.players) < self.capacity

    def add(self, player):
        self.players.append(player)

    def remove(self, player):
        self.players.remove(player)


class Room(Space):
    def __init__(self, room_type: RoomType):
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
        self.grid = [
            [Room(RoomType.STUDY), Hallway(), Room(RoomType.HALL), Hallway(), Room(RoomType.LOUNGE)],
            [Hallway(), Void(), Hallway(), Void(), Hallway()],
            [Room(RoomType.LIBRARY), Hallway(), Room(RoomType.BILLIARD), Hallway(), Room(RoomType.DINING)],
            [Hallway(), Void(), Hallway(), Void(), Hallway()],
            [Room(RoomType.CONSERVATORY), Hallway(), Room(RoomType.BALLROOM), Hallway(), Room(RoomType.KITCHEN)]
        ]

    def move_in_direction(self, player, direction):
        try:
            new_position = self.__calculate_new_position(player.position, direction)
            self.move(player, new_position)
        except:
            print("Error: Cannot move in direction")

    def move(self, player, position):
        if not self.grid[position[0]][position[1]].can_add():
            print("Error: Cannot add player to space")
            return
        from_position = player.position
        self.grid[from_position[0]][from_position[1]].remove(player)
        self.grid[position[0]][position[1]].add(player)
        player.set_position(position)

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
                new_position = (from_position[0], from_position - 1)
            case Direction.RIGHT if from_position[1] < 4:
                new_position = (from_position[0], from_position + 1)
            case Direction.SECRET_PASSAGEWAY if from_position == (0, 0) or from_position == (4, 4):
                new_position = (4 - from_position[0], 4 - from_position[1])
            case Direction.SECRET_PASSAGEWAY if from_position == (0, 4) or from_position == (4, 0):
                new_position = (from_position[1], from_position[0])
            case _:
                raise ValueError("Invalid direction")
        return new_position
