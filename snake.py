# import random
from a_star import BattlesnakeAStarPathfinder


class Battlesnake:
    def __init__(self):
        self.apiversion = "1"
        self.author = "bvanvugt"
        self.version = "v4"
        self.color = "#36627b"
        self.head = "silly"
        self.tail = "curled"

    def move(self, request):
        turn = request["turn"]

        move = "up"
        possible_moves = self._calc_possible_moves(request)
        if possible_moves:
            targets = self._calc_targets(request)
            move = self._calc_best_move(request, possible_moves, targets)

        print(f"{turn}: {possible_moves} -> {move}")
        return move

    def _calc_possible_moves(self, request):
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

        # Remove our necks from possible moves
        for snake in request["board"]["snakes"]:
            necks = snake["body"][:-1]

            # This code removes moves that may collide with
            # next moves of other snakes. These moves are
            # technically possible, and shouldn't be removed in
            # this func...

            if snake["length"] > request["you"]["length"]:
                snake_head = snake["body"][0]
                necks.extend(
                    [
                        {"x": snake_head["x"] - 1, "y": snake_head["y"]},
                        {"x": snake_head["x"] + 1, "y": snake_head["y"]},
                        {"x": snake_head["x"], "y": snake_head["y"] - 1},
                        {"x": snake_head["x"], "y": snake_head["y"] + 1},
                    ]
                )

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

    def _calc_move_coords(self, coords, move):
        if move == "up":
            return {"x": coords["x"], "y": coords["y"] + 1}
        if move == "down":
            return {"x": coords["x"], "y": coords["y"] - 1}
        if move == "right":
            return {"x": coords["x"] + 1, "y": coords["y"]}
        return {"x": coords["x"] - 1, "y": coords["y"]}

    def _calc_distance_manhattan(self, p1, p2):
        return abs(p1["x"] - p2["x"]) + abs(p1["y"] - p2["y"])

    def _calc_distance(self, p1, p2):
        return self._calc_distance_manhattan(p1, p2)

    def _calc_closest_coord(
        self, current_coords, other_coords, actually_furthest=False
    ):
        distances = []
        for coords in other_coords:
            d = self._calc_distance(current_coords, coords)
            distances.append((coords, d))
        distances.sort(key=lambda x: x[1], reverse=actually_furthest)
        return distances[0][0]

    def _order_by_distance(self, start_coords, targets):
        distances = []
        for coords in targets:
            d = self._calc_distance(start_coords, coords)
            distances.append((coords, d))
        distances.sort(key=lambda x: x[1])
        return [d[0] for d in distances]

    def _calc_astar(self, request, start_coords, end_coords):
        astar_solver = BattlesnakeAStarPathfinder(request["board"])
        st = (start_coords["x"], start_coords["y"])
        et = (end_coords["x"], end_coords["y"])
        return astar_solver.astar(st, et)

    def _calc_path_exists(self, request, start_coords, end_coords, debug=False):
        astar_path = self._calc_astar(request, start_coords, end_coords)
        if debug:
            print(f"  A*: {start_coords}, {end_coords}, {astar_path}")
        return astar_path is not None

    def _calc_path_length(self, request, start_coords, end_coords):
        astar_path = self._calc_astar(request, start_coords, end_coords)
        if astar_path:
            return len(list(astar_path))
        return None

    def _calc_targets(self, request):
        targets = []

        head_coords = request["you"]["head"]
        tail_coords = request["you"]["body"][-1]
        # closest_food = self._calc_closest_coord(head_coords, request["board"]["food"])
        ordered_food = self._order_by_distance(head_coords, request["board"]["food"])

        our_length = request["you"]["length"]
        max_opponent_length = max(
            [
                s["length"]
                for s in request["board"]["snakes"]
                if s["id"] != request["you"]["id"]
            ]
        )
        if our_length < (max_opponent_length + 2):
            print(" HUNGRY")
            # We're hungry
            for food_coords in ordered_food:
                # TODO: This doesn't work when we just ate because our tail is doubled and thus untraversable.
                if self._calc_path_exists(
                    request, food_coords, tail_coords, debug=True
                ):
                    print(f"  FOOD: {food_coords}")
                    targets.append(food_coords)

        # if request["you"]["health"] <= 50:
        #     if self._calc_path_exists(request, closest_food, tail_coords):
        #         targets.append(closest_food)

        targets.append(tail_coords)
        targets.append({"x": tail_coords["x"] + 1, "y": tail_coords["y"]})
        targets.append({"x": tail_coords["x"] - 1, "y": tail_coords["y"]})
        targets.append({"x": tail_coords["x"], "y": tail_coords["y"] + 1})
        targets.append({"x": tail_coords["x"], "y": tail_coords["y"] - 1})

        corners = [
            {"x": 0, "y": 0},
            {"x": 0, "y": request["board"]["height"] - 1},
            {"x": request["board"]["width"] - 1, "y": 0},
            {"x": request["board"]["width"] - 1, "y": request["board"]["height"] - 1},
        ]
        for corner_coords in corners:
            if self._calc_path_exists(request, corner_coords, tail_coords):
                targets.append(corner_coords)

        return targets

    def _calc_best_move(self, request, moves, targets):
        head_coords = request["you"]["head"]

        for target_coords in targets:
            print(f" TARGET -> {target_coords}")

            distance_moves = []
            for move in moves:
                move_coords = self._calc_move_coords(head_coords, move)
                astar_path_length = self._calc_path_length(
                    request, move_coords, target_coords
                )
                if astar_path_length:
                    distance_moves.append((move, astar_path_length))

            if distance_moves:
                distance_moves.sort(key=lambda x: x[1])
                return distance_moves[0][0]

        if moves:
            return moves[0]

        print("   NO VALID MOVES TO ALL TARGETS")
        return "up"
