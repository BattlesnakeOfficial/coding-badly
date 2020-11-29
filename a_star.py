from astar import AStar


class BattlesnakeAStarPathfinder(AStar):
    def __init__(self, board, target=None, force_target_traversible=False):
        self._board = board

        self._target = target
        self._force_target_traversible = force_target_traversible

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
            if self._target and self._force_target_traversible:
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
