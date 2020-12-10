from astar import AStar


def calc_possible_moves(request):
    possible_moves = ["up", "down", "left", "right"]

    def remove_move(move):
        if move in possible_moves:
            possible_moves.remove(move)

    head = request["you"]["body"][0]

    # Remove oob from possible moves
    if head["x"] == 0:
        remove_move("left")
    if head["y"] == 0:
        remove_move("down")
    if head["x"] == request["board"]["width"] - 1:
        remove_move("right")
    if head["y"] == request["board"]["height"] - 1:
        remove_move("up")

    # Remove all snake bodies, excluding tails, from possible moves
    for snake in request["board"]["snakes"]:
        necks = snake["body"][:-1]
        for neck in necks:
            if (neck["x"] == head["x"] + 1) and (neck["y"] == head["y"]):
                remove_move("right")
            if (neck["x"] == head["x"] - 1) and (neck["y"] == head["y"]):
                remove_move("left")
            if (neck["x"] == head["x"]) and (neck["y"] == head["y"] + 1):
                remove_move("up")
            if (neck["x"] == head["x"]) and (neck["y"] == head["y"] - 1):
                remove_move("down")

    return possible_moves


def calc_next_move(request, current_coords, target_coords):
    st = (current_coords["x"], current_coords["y"])
    et = (target_coords["x"], target_coords["y"])
    astar_solver = BattlesnakeAStarPathfinder(request["board"], target_coords)
    path = astar_solver.astar(st, et)
    if path:
        path_tuples = list(path)
        if len(path_tuples) > 1:
            next_tuple = path_tuples[1]
            next_coords = {"x": next_tuple[0], "y": next_tuple[1]}

            if next_coords["x"] > current_coords["x"]:
                return "right"
            if next_coords["x"] < current_coords["x"]:
                return "left"
            if next_coords["y"] > current_coords["y"]:
                return "up"
            if next_coords["y"] < current_coords["y"]:
                return "down"
            assert False

    return None


class BattlesnakeAStarPathfinder(AStar):
    def __init__(self, board, target_coords):
        self._board = board
        self._target = (target_coords["x"], target_coords["y"])

    def heuristic_cost_estimate(self, n1, n2):
        # Manhattan
        return abs(n1[0] - n2[0]) + abs(n1[1] - n2[1])

    def distance_between(self, n1, n2):
        return 1

    def neighbors(self, node):
        possible_neighbors = [
            (node[0] + 1, node[1]),
            (node[0] - 1, node[1]),
            (node[0], node[1] + 1),
            (node[0], node[1] - 1),
        ]

        actual_neighbors = []
        for possible_neighbor in possible_neighbors:
            # Assume target is always traversible
            if possible_neighbor == self._target:
                actual_neighbors.append(possible_neighbor)
                continue

            if possible_neighbor[0] < 0:
                continue
            if possible_neighbor[0] >= self._board["width"]:
                continue
            if possible_neighbor[1] < 0:
                continue
            if possible_neighbor[1] >= self._board["height"]:
                continue

            occupied = False
            for snake in self._board["snakes"]:
                for snake_coords in snake["body"][:-1]:
                    snake_tuple = (snake_coords["x"], snake_coords["y"])
                    if possible_neighbor == snake_tuple:
                        occupied = True

            if not occupied:
                actual_neighbors.append(possible_neighbor)

        # print(f" NBORS: {node}, {actual_neighbors}")
        return actual_neighbors
