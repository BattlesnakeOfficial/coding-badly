def is_coords_open(board, coords):
    if coords["x"] < 0:
        return False
    if coords["x"] >= board["width"]:
        return False
    if coords["y"] < 0:
        return False
    if coords["y"] >= board["height"]:
        return False

    for snake in board["snakes"]:
        for snake_coords in snake["body"]:
            if snake_coords == coords:
                return False

    return True


def calc_neighbors(coords):
    return [
        {"x": coords["x"], "y": coords["y"] + 1},
        {"x": coords["x"], "y": coords["y"] - 1},
        {"x": coords["x"] + 1, "y": coords["y"]},
        {"x": coords["x"] - 1, "y": coords["y"]},
    ]


def calc_open_space(board, coords):
    if not is_coords_open(board, coords):
        return 0

    open_coords = [coords]
    seen_coords = []

    while len(open_coords) > 0:
        c = open_coords.pop(0)
        seen_coords.append(c)

        neighbors = calc_neighbors(c)
        for neighbor in neighbors:
            if neighbor in seen_coords:
                continue
            if not is_coords_open(board, neighbor):
                continue
            if neighbor not in open_coords:
                open_coords.append(neighbor)

    return len(seen_coords)
