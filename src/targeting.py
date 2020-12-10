import floodfill
import util


def calc_targets(request):
    targets = []

    head_coords = request["you"]["head"]

    ordered_food = sorted(
        request["board"]["food"],
        key=lambda x: util.calc_manhattan_distance(head_coords, x),
    )

    food_scores = []
    for food_coords in ordered_food + [request["you"]["body"][-1]]:
        score = floodfill.calc_open_space(request["board"], food_coords)
        food_scores.append((food_coords, score))
    food_scores.sort(key=lambda x: x[1], reverse=True)
    for food_score in food_scores:
        targets.append(food_score[0])

    moves_required = 0
    reversed_body = request["you"]["body"][::-1]
    for self_coords in reversed_body:
        targets.append(self_coords)
        moves_required += 1

    return targets
