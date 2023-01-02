from board import Direction, Rotation, Action, Shape
from random import Random
from time import sleep
from constants import DEFAULT_SEED
# GENETIC CODE
from adversary import RandomAdversary
from board import Board, Direction, Rotation, Action, Shape
from constants import BOARD_WIDTH, BOARD_HEIGHT, DEFAULT_SEED, INTERVAL, BLOCK_LIMIT
from exceptions import BlockLimitException
from math import *
from random import *
import os

global agg_weight
global complete_weight
global holes_weight
global bump_weight
# PLAYER


def rotation_coords_list(board, start):  # 0=column, 1=row
    if board.falling.shape == Shape.O:
        return [[(start[0], start[1]), (start[0], start[1] - 1), (start[0] + 1, start[1] - 1),
                 (start[0] + 1, start[1])]], [0]
    if board.falling.shape == Shape.I:
        return [[(start[0], start[1]), (start[0] + 1, start[1]), (start[0] + 2, start[1]), (start[0] + 3, start[1])],
                # change
                [(start[0], start[1]), (start[0], start[1] - 3), (start[0], start[1] - 1), (start[0], start[1] - 2)]], \
               [1, 0]
    if board.falling.shape == Shape.S:
        return [[(start[0], start[1]), (start[0] + 1, start[1]), (start[0] + 1, start[1] - 1),
                 (start[0] + 2, start[1] - 1)],  # change
                [(start[0], start[1] - 1), (start[0], start[1] - 2), (start[0] + 1, start[1]),
                 (start[0] + 1, start[1] - 1)]], [0, 1]
    if board.falling.shape == Shape.Z:
        return [[(start[0], start[1]), (start[0] + 1, start[1]), (start[0], start[1] - 1),
                 (start[0] - 1, start[1] - 1)],  # change
                [(start[0], start[1]), (start[0], start[1] - 1), (start[0] + 1, start[1] - 1),
                 (start[0] + 1, start[1] - 2)]], [0, 1]
    if board.falling.shape == Shape.J:
        return [[(start[0], start[1]), (start[0], start[1] - 1), (start[0] + 1, start[1]),
                 (start[0] + 2, start[1])],
                [(start[0], start[1]), (start[0], start[1] - 1), (start[0] - 1, start[1] - 1),
                 (start[0] - 2, start[1] - 1)],  # change
                [(start[0], start[1]), (start[0] + 1, start[1]), (start[0] + 1, start[1] - 1),
                 (start[0] + 1, start[1] - 2)],  # change
                [(start[0], start[1]), (start[0], start[1] - 1), (start[0], start[1] - 2),
                 (start[0] + 1, start[1] - 2)]], [1, -1, 0, 2]  # change
    if board.falling.shape == Shape.L:
        return [[(start[0], start[1]), (start[0] + 1, start[1]), (start[0] + 2, start[1]),
                 (start[0] + 2, start[1] - 1)],
                [(start[0], start[1]), (start[0], start[1] - 1), (start[0] + 1, start[1] - 1),
                 (start[0] + 2, start[1] - 1)],  # change
                [(start[0], start[1]), (start[0] + 1, start[1]), (start[0], start[1] - 1),
                 (start[0], start[1] - 2)],  # change
                [(start[0], start[1]), (start[0], start[1] - 1), (start[0], start[1] - 2),
                 (start[0] - 1, start[1] - 2)]], [-1, 1, 0, 2]  # change
    if board.falling.shape == Shape.T:
        return [[(start[0], start[1]), (start[0] + 1, start[1]), (start[0] + 1, start[1] - 1),
                 (start[0] + 2, start[1])],
                [(start[0], start[1]), (start[0] - 1, start[1] - 1), (start[0] + 1, start[1] - 1),
                 (start[0], start[1] - 1)],  # change
                [(start[0], start[1]), (start[0], start[1] - 1), (start[0] - 1, start[1] - 1),
                 (start[0], start[1] - 2)],  # change
                [(start[0], start[1]), (start[0], start[1] - 1), (start[0] + 1, start[1] - 1),
                 (start[0], start[1] - 2)]], [2, 0, 1, -1]  # change
    if board.falling.shape == Shape.B:
        return []


def get_max_height(board):
    height = get_base_ind_heights(board)
    return max(height)


def check_for_out_of_bounds(possibilities):
    for j in range(4):
        # print("(", possibilities[j][0], ",", possibilities[j][1], ")", end=" ")
        if possibilities[j][1] < 0 or possibilities[j][1] > 23:
            # print(False)
            return False
        if possibilities[j][0] < 0 or possibilities[j][0] > 9:
            # print(False)
            return False
    # print(True)
    return True


def collision_check(possibilities, board):
    for j in range(4):
        if possibilities[j] in board.cells:
            return False
    return True


def get_base_ind_heights(board):
    height_list = [23] * 10
    for column in range(10):
        for (column_id2, row_id2) in board.cells:
            if column_id2 == column:
                if row_id2 - 1 < height_list[column]:
                    height_list[column] = row_id2 - 1
        height_list[column] = 23 - height_list[column]
    return height_list


def get_ind_heights(board, possibility):
    height_list = [23] * 10
    for column in range(10):
        for (column_id, row_id) in possibility:
            if column_id == column:
                if row_id - 1 < height_list[column]:
                    height_list[column] = row_id - 1
        for (column_id2, row_id2) in board.cells:
            if column_id2 == column:
                if row_id2 - 1 < height_list[column]:
                    height_list[column] = row_id2 - 1
        height_list[column] = 23 - height_list[column]
    return height_list


def aggregate_height(board, possibility):
    height_list = get_ind_heights(board, possibility)
    agg_height = 0
    for column in range(10):
        agg_height += height_list[column]
    return agg_height


def complete_lines(board, possibility):
    c_lines = 0
    for row in range(24):
        marker = True
        for column in range(10):
            if (column, row) not in board.cells and (column, row) not in possibility:
                marker = False
                break
        if marker:
            c_lines += 1
    return c_lines


def landlock_count(board, possibility):
    land_count = 0
    height_list = get_ind_heights(board, possibility)
    for column in range(10):
        for row in range(23 - height_list[column] + 1, 23):
            if (column, row + 1) not in board.cells and (column, row + 1) not in possibility:
                land_count += 1
    return land_count


def bumpiness(board, possibility):
    list_heights = get_ind_heights(board, possibility)
    bumps = [0] * 9
    #bumps[0] = list_heights[0]
    for i in range(9):
        bumps[i] = abs(list_heights[i] - list_heights[i + 1])
    bump = 0
    for i in range(9):
        bump += bumps[i]
    #bump += list_heights[9]
    return bump


def adjacent(pos, next_pos):
    if (pos[0] - 1 == next_pos[0] or pos[0] + 1 == next_pos[0]) and (pos[1] == next_pos[1]):
        return True
    if (pos[1] - 1 == next_pos[1] or pos[1] + 1 == next_pos[1]) and (pos[0] == next_pos[0]):
        return True
    return False


def blockades(board, possibility):
    holes = []
    height_list = get_ind_heights(board, possibility)
    blockade_count = 0
    for column in range(10):
        for row in range(23 - height_list[column] + 1, 23):
            if (column, row + 1) not in board.cells and (column, row + 1) not in possibility:
                holes.append((column, row + 1))
    print(holes)
    if len(holes) < 2:
        for i in range(len(holes) - 1):
            blockade_count += 1
            while adjacent(holes[i], holes[i + 1]):
                i += 1
    return blockade_count


def collisions_underneath(board, possibility):
    for j in range(4):
        # print(possibility[j])
        if (possibility[j][0], possibility[j][1] - 1) in board.cells:
            return False
    return True

# agg_weight = -0.2
# complete_weight = 0
# holes_weight = -5
# bump_weight = -0.9
# blockades_weight = -5.2


def score_calc(board, possibility):
    # global agg_weight
    # global complete_weight
    # global holes_weight
    # global bump_weight
    # print(blockades(board, possibility))
    agg_weight = -7.6
    complete_weight = 8.6
    holes_weight = -11.9
    bump_weight = -4.1
    # print(agg_weight, complete_weight, holes_weight, bump_weight)
    # print(aggregate_height(board, possibility), complete_lines(board, possibility), landlock_count(board, possibility), bumpiness(board, possibility))
    # print(blockades(board, possibility), end =" ")
    score = agg_weight * aggregate_height(board, possibility)
    score += complete_weight * complete_lines(board, possibility)
    score += holes_weight * landlock_count(board, possibility)
    score += bump_weight * bumpiness(board, possibility)
    return score


def row_by_row_solver(board):
    # max_height = get_max_height(board)
    possibilities_list = []
    rotations_list = []
    scores = []
    for row in range(23, 0, -1):
        # print("column start")
        for column in range(10):
            # not occupied check
            if (column, row) not in board.cells:
                possibilities, rotation = rotation_coords_list(board, (column, row))
                # print("possibilities for column start", column)
                for i in range(len(possibilities)):
                    # print(possibilities[i], rotation[i])
                    # out of bounds check
                    if check_for_out_of_bounds(possibilities[i]) and collision_check(possibilities[i], board):
                        if collisions_underneath(board, possibilities[i]):
                            # print("actual", possibilities[i])
                            possibilities_list.append(possibilities[i])
                            rotations_list.append(rotation[i])
                            scores.append(score_calc(board, possibilities[i]))
                # print("possibilities for column end", column)
        # if len(possibilities_list) != 0:
            # print(possibilities_list, rotations_list)
    max_score = 0
    for i in range(1, len(scores)):
        if scores[i] > scores[max_score]:
            max_score = i
    return possibilities_list[max_score], rotations_list[max_score]


class Player:
    def __init__(self):
        self.test = 0
        self.directionCount = 0
        self.rotationCount = 0
        print(DEFAULT_SEED)

    def print_board(self, board):
        print("--------")
        for y in range(24):
            s = ""
            for x in range(10):
                if (x, y) in board.cells:
                    s += "#"
                else:
                    s += "."
            print(s, y)

    def choose_action(self, board):
        # print(DEFAULT_SEED)
        possibility, rotation = row_by_row_solver(board)
        if rotation < 0:
            yield Rotation.Anticlockwise
        else:
            for rotate in range(rotation):
                yield Rotation.Clockwise
        current_pos = list(sorted(board.falling.cells))[0]
        end_pos = sorted(possibility)[0]
        # print(sorted(board.falling.cells), sorted(possibility), board.falling.shape, current_pos, end_pos)
        if current_pos[0] == end_pos[0]:
            yield Direction.Drop
        elif current_pos[0] > end_pos[0]:
            t = current_pos[0] - end_pos[0]
            for times in range(t):
                yield Direction.Left
            yield Direction.Drop
        elif current_pos[0] < end_pos[0]:
            t = end_pos[0] - current_pos[0]
            for times in range(t):
                yield Direction.Right
            yield Direction.Drop


SelectedPlayer = Player


# GENETIC


def random_integer(minimum, maximum):
    return floor(random() * (maximum - minimum) + minimum)


def normalize(candidate2):
    norm = sqrt(candidate2["agg_weight"] * candidate2["agg_weight"] + candidate2["complete_weight"] * candidate2[
        "complete_weight"] + candidate2["holes_weight"] * candidate2["holes_weight"] + candidate2["bump_weight"] *
                candidate2["bump_weight"])
    candidate2["agg_weight"] /= norm
    candidate2["complete_weight"] /= norm
    candidate2["holes_weight"] /= norm
    candidate2["bump_weight"] /= norm
    candidate2["agg_weight"] *= 10
    candidate2["complete_weight"] *= 10
    candidate2["holes_weight"] *= 10
    candidate2["bump_weight"] *= 10


def generate_random_candidate():
    candidate2 = {"agg_weight": random() * random_integer(-10, 0) - 0.5,
                  "complete_weight": random() * random_integer(0, 10) - 0.5,
                  "holes_weight": random() * random_integer(-10, 0) - 0.5,
                  "bump_weight": random() * random_integer(-10, 0) - 0.5,
                  "fitness": None}
    normalize(candidate2)
    return candidate2


def compute_fitnesses(candidates2, number_of_games):
    for i in range(len(candidates2)):
        candidate2 = candidates2[i]
        totalscore = 0
        global agg_weight
        global complete_weight
        global holes_weight
        global bump_weight
        agg_weight = candidate2["agg_weight"]
        complete_weight = candidate2["complete_weight"]
        holes_weight = candidate2["holes_weight"]
        bump_weight = candidate2["bump_weight"]
        for j in range(number_of_games):
            score = run()
            totalscore += score

        print(totalscore, end=" ")
        candidate2["fitness"] = totalscore


def sort(candidates2):
    n = len(candidates2)
    for i in range(n):
        already_sorted = True
        for j in range(n - i - 1):
            if candidates2[j]["fitness"] < candidates2[j + 1]["fitness"]:
                temp = candidates2[j]
                candidates2[j] = candidates2[j + 1]
                candidates2[j + 1] = temp
                already_sorted = False
        if already_sorted:
            break
    return candidates2


def tournament_select_pair(candidates2, ways):
    indices = []
    for i in range(len(candidates2)):
        indices.append(i)
    fittest_candidate_index_1 = None
    fittest_candidate_index_2 = None
    for i in range(ways):
        indices = indices[random_integer(0, len(indices)):len(indices)]
        selected_index = indices[0]
        if fittest_candidate_index_1 is None or selected_index < fittest_candidate_index_1:
            fittest_candidate_index_2 = fittest_candidate_index_1
            fittest_candidate_index_1 = selected_index
        elif fittest_candidate_index_2 is None or selected_index < fittest_candidate_index_2:
            fittest_candidate_index_2 = selected_index
    return [candidates2[fittest_candidate_index_1], candidates2[fittest_candidate_index_2]]


def cross_over(candidate1, candidate2):
    candidate_copy = {
        "agg_weight": candidate1["fitness"] * candidate1["agg_weight"] + candidate2["fitness"] * candidate2[
            "agg_weight"],
        "complete_weight": candidate1["fitness"] * candidate1["complete_weight"] + candidate2["fitness"] * candidate2[
            "complete_weight"],
        "holes_weight": candidate1["fitness"] * candidate1["holes_weight"] + candidate2["fitness"] * candidate2[
            "holes_weight"],
        "bump_weight": candidate1["fitness"] * candidate1["agg_weight"] + candidate2["fitness"] * candidate2[
            "bump_weight"],
        "fitness": None
    }
    normalize(candidate_copy)
    return candidate_copy


def mutate(candidate2):
    quantity = random() * 0.4 - 0.2
    rand_num = randint(0, 4)
    if rand_num == 0:
        candidate2["agg_weight"] += quantity
    elif rand_num == 1:
        candidate2["complete_weight"] += quantity
    elif rand_num == 2:
        candidate2["holes_weight"] += quantity
    elif rand_num == 3:
        candidate2["bump_weight"] += quantity


def delete_n_last_replacement(candidates2, new_candidates2):
    # diff = len(new_candidates2) - len(candidates2)
    candidates2 = candidates2[:-len(new_candidates2)]
    for i in range(len(new_candidates)):
        candidates2.append(new_candidates[i])
    candidates2 = sort(candidates2)
    return candidates2


def run():
    DEFAULT_SEED_2 = randint(0, 8589724859373205897243985)
    board = Board(BOARD_WIDTH, BOARD_HEIGHT)
    adversary = RandomAdversary(DEFAULT_SEED_2, BLOCK_LIMIT)
    player = SelectedPlayer()
    try:
        for move in board.run(player, adversary):
            pass
        # print("Score=", board.score)
    except BlockLimitException:
        # print("Out of blocks")
        # print("Score=", board.score)
        pass
    except KeyboardInterrupt:
        pass
    return board.score


if __name__ == '__main__':
    population = 10
    rounds = 2
    candidates = []
    for i2 in range(population):
        candidates.append(generate_random_candidate())
    print("Computing fitnesses of initial population")
    compute_fitnesses(candidates, rounds)
    print("computing Done")
    candidates = sort(candidates)
    print("sorting done")
    print(candidates)
    count = 0

    while True:
        new_candidates = []
        popu = int(0.5 * population)  # percent of population
        for i2 in range(popu):
            pair = tournament_select_pair(candidates, 10)
            candidate = cross_over(pair[0], pair[1])
            if random() < 0.05:  # 5% mutation
                mutate(candidate)
            normalize(candidate)
            new_candidates.append(candidate)
        print("Computing fitnesses of new candidates. (" + str(count) + ")")
        compute_fitnesses(new_candidates, rounds)
        #print(new_candidates)
        candidates = delete_n_last_replacement(candidates, new_candidates)
        print(candidates)
        total_fitness = 0
        for i2 in range(len(candidates)):
            total_fitness += (candidates[i2]["fitness"]/rounds)
        print("")
        print("Average Fitness = " + str(total_fitness / len(candidates)))
        print("Highest Fitness = " + str(candidates[0]["fitness"]/rounds) + " (" + str(count) + ") ")
        print("Fittest Candidate = " + str(candidates[0]) + " (" + str(count) + ") ")
        count += 1
