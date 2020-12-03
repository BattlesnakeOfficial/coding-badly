# import random
from a_star import BattlesnakeAStarPathfinder


class Battlesnake:
    def __init__(self):
        self.apiversion = "1"
        self.author = "bvanvugt"
        self.version = "Day 5"
        self.color = "#36627b"
        self.head = "silly"
        self.tail = "curled"

    def move(self, request):
        turn = request["turn"]
        print(f"\n{turn}")

        move = "up"
        possible_moves = self._calc_possible_moves(request)
        if possible_moves:
            targets = self._calc_targets(request)
            move = self._calc_best_move(request, possible_moves, targets)

        print(f"{turn}: {possible_moves} -> {move}")
        return move

    def _calc_possible_moves(self, request):
        risk = {"up": 0, "down": 0, "left": 0, "right": 0}

        head = request["you"]["body"][0]

        # Remove oob from possible moves
        if head["x"] == 0:
            risk["left"] = 100
        if head["y"] == 0:
            risk["down"] = 100
        if head["x"] == request["board"]["width"] - 1:
            risk["right"] = 100
        if head["y"] == request["board"]["height"] - 1:
            risk["up"] = 100

        # Remove our necks from possible moves
        for snake in request["board"]["snakes"]:
            necks = snake["body"][:-1]

            for neck in necks:
                if (neck["x"] == head["x"] + 1) and (neck["y"] == head["y"]):
                    risk["right"] = 100
                if (neck["x"] == head["x"] - 1) and (neck["y"] == head["y"]):
                    risk["left"] = 100
                if (neck["x"] == head["x"]) and (neck["y"] == head["y"] + 1):
                    risk["up"] = 100
                if (neck["x"] == head["x"]) and (neck["y"] == head["y"] - 1):
                    risk["down"] = 100

            # This code removes moves that may collide with
            # next moves of other snakes. These moves are
            # technically possible, and shouldn't be removed in
            # this func...

            if snake["length"] > request["you"]["length"]:
                # We'll lose head-to-head
                snake_head = snake["body"][0]
                necks = [
                    {"x": snake_head["x"] - 1, "y": snake_head["y"]},
                    {"x": snake_head["x"] + 1, "y": snake_head["y"]},
                    {"x": snake_head["x"], "y": snake_head["y"] - 1},
                    {"x": snake_head["x"], "y": snake_head["y"] + 1},
                ]

                for neck in necks:
                    if (neck["x"] == head["x"] + 1) and (neck["y"] == head["y"]):
                        risk["right"] = max(risk["right"], 50)
                    if (neck["x"] == head["x"] - 1) and (neck["y"] == head["y"]):
                        risk["left"] = max(risk["left"], 50)
                    if (neck["x"] == head["x"]) and (neck["y"] == head["y"] + 1):
                        risk["up"] = max(risk["up"], 50)
                    if (neck["x"] == head["x"]) and (neck["y"] == head["y"] - 1):
                        risk["down"] = max(risk["down"], 50)

        sorted_risks = [
            (x[0], x[1]) for x in sorted(risk.items(), key=lambda x: x[1]) if x[1] < 100
        ]
        sorted_moves = []
        for i in range(100):
            move_group = []
            for sorted_risk in sorted_risks:
                if sorted_risk[1] == i:
                    move_group.append(sorted_risk[0])
            if len(move_group) > 0:
                sorted_moves.append(move_group)
        print(sorted_moves)
        return sorted_moves

        # sorted_moves = [
        #     x[0] for x in
        #     sorted(risk.items(), key=lambda x: x[1])
        #     if x[1] < 100
        # ]
        # return sorted_moves

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

    def _calc_astar(
        self, request, start_coords, end_coords, force_target_traversible=False
    ):
        st = (start_coords["x"], start_coords["y"])
        et = (end_coords["x"], end_coords["y"])
        astar_solver = BattlesnakeAStarPathfinder(
            request["board"],
            target=et,
            force_target_traversible=force_target_traversible,
        )
        return astar_solver.astar(st, et)

    def _calc_path_exists(
        self,
        request,
        start_coords,
        end_coords,
        force_target_traversible=False,
        debug=False,
    ):
        astar_path = self._calc_astar(
            request, start_coords, end_coords, force_target_traversible
        )
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

        for snake in request["board"]["snakes"]:
            if snake["length"] < request["you"]["length"]:
                targets.append(snake["head"])

        head_coords = request["you"]["head"]
        tail_coords = request["you"]["body"][-1]
        ordered_food = self._order_by_distance(head_coords, request["board"]["food"])

        our_length = request["you"]["length"]
        max_opponent_length = our_length
        if len(request["board"]["snakes"]) > 1:
            max_opponent_length = max(
                [
                    s["length"]
                    for s in request["board"]["snakes"]
                    if s["id"] != request["you"]["id"]
                ]
            )
        if our_length < (max_opponent_length + 2):
            print(" HUNGRY")  # We're hungry
            for food_coords in ordered_food:
                if self._calc_path_exists(
                    request,
                    food_coords,
                    tail_coords,
                    force_target_traversible=True,
                    debug=True,
                ):
                    is_another_snake_closer = False
                    our_turns_to_food = self._calc_path_length(
                        request, head_coords, food_coords
                    )
                    for snake in request["board"]["snakes"]:
                        other_turns_to_food = self._calc_path_length(
                            request, snake["head"], food_coords
                        )
                        if not other_turns_to_food:
                            continue

                        is_closer = other_turns_to_food < our_turns_to_food
                        is_bigger = snake["length"] > request["you"]["length"]
                        if is_closer or (
                            is_bigger
                            and other_turns_to_food
                            and our_turns_to_food == other_turns_to_food
                        ):
                            is_another_snake_closer = True
                    if not is_another_snake_closer:
                        print(f"  FOOD: {food_coords}")
                        targets.append(food_coords)

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

        # Try to chase other snake tails
        for snake in request["board"]["snakes"]:
            if snake["id"] == request["you"]["id"]:
                continue
            targets.append(snake["body"][-1])

        return targets

    def _calc_best_move(self, request, move_groups, targets):
        head_coords = request["you"]["head"]

        for target_coords in targets:
            print(f" TARGET -> {target_coords}")

            for move_group in move_groups:
                distance_moves = []
                for move in move_group:
                    move_coords = self._calc_move_coords(head_coords, move)
                    astar_path_length = self._calc_path_length(
                        request, move_coords, target_coords
                    )
                    if astar_path_length:
                        distance_moves.append((move, astar_path_length))

                if distance_moves:
                    distance_moves.sort(key=lambda x: x[1])
                    return distance_moves[0][0]

        if move_groups:
            if move_groups[0]:
                return move_groups[0][0]

        print("   NO VALID MOVES TO ALL TARGETS")
        return "up"
