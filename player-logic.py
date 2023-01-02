from board import Direction, Rotation, Action, Shape
from random import Random
from time import sleep
from constants import DEFAULT_SEED

agg_weight = -7
complete_weight = 8.6
# complete_weight = 0
# holes_weight = -6.7
holes_weight = -11.5
#holes_weight = -7.6
bump_weight = -4.1
# bump_weight = -3
# blockades_weight = -5.2


def check_if_rows_are_ready(board, row_id):
    for row in range(row_id, row_id + 5):
        for column in range(0, 9):
            if (column, row) not in board.cells:
                return False
    return True


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


def check_for_out_of_bounds(possibilities, possibilities2=None):
    if possibilities2 is None:
        for j in range(4):
            if possibilities[j][1] < 0 or possibilities[j][1] > 23:
                return False
            if possibilities[j][0] < 0 or possibilities[j][0] > 9:
                return False
        return True
    else:
        for j in range(4):
            if possibilities2[j][1] < 0 or possibilities2[j][1] > 23:
                return False
            if possibilities2[j][0] < 0 or possibilities2[j][0] > 9:
                return False
        return True


def collision_check(possibilities, board, possibilities2=None):
    if possibilities2 is None:
        for j in range(4):
            if possibilities[j] in board.cells:
                return False
        return True
    else:
        for j in range(4):
            if possibilities2[j] in board.cells:
                return False
            if possibilities2[j] in possibilities:
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


def get_ind_heights(board, possibility, possibility2=None):
    if possibility2 is None:
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
    else:
        height_list = [23] * 10
        for column in range(10):
            for (column_id, row_id) in possibility2:
                if column_id == column:
                    if row_id - 1 < height_list[column]:
                        height_list[column] = row_id - 1
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


def aggregate_height(board, possibility, possibility2=None):
    if possibility2 is None:
        height_list = get_ind_heights(board, possibility)
        agg_height = 0
        for column in range(10):
            agg_height += height_list[column]
        return agg_height
    else:
        height_list = get_ind_heights(board, possibility, possibility2)
        agg_height = 0
        for column in range(10):
            agg_height += height_list[column]
        return agg_height


def complete_lines(board, possibility, possibility2=None):
    if possibility2 is None:
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
    else:
        c_lines = 0
        for row in range(24):
            marker = True
            for column in range(10):
                if (column, row) not in board.cells and (column, row) not in possibility and (column, row) not in possibility2:
                    marker = False
                    break
            if marker:
                c_lines += 1
        return c_lines


def holes_count(board, possibility, possibility2=None):
    if possibility2 is None:
        land_count = 0
        height_list = get_ind_heights(board, possibility)
        for column in range(10):
            for row in range(23 - height_list[column], 23):
                if (column, row + 1) not in board.cells and (column, row + 1) not in possibility:
                    land_count += 1
        return land_count
    else:
        land_count = 0
        height_list = get_ind_heights(board, possibility)
        for column in range(10):
            for row in range(23 - height_list[column], 23):
                if (column, row + 1) not in board.cells and (column, row + 1) not in possibility and (column, row + 1) not in possibility2:
                    land_count += 1
        return land_count


def bumpiness(board, possibility, possibility2=None):
    if possibility2 is None:
        list_heights = get_ind_heights(board, possibility)
        bumps = [0] * 9
        for i in range(9):
            bumps[i] = abs(list_heights[i] - list_heights[i + 1])
        bump = 0
        for i in range(9):
            bump += bumps[i]
        return bump
    else:
        list_heights = get_ind_heights(board, possibility, possibility2)
        bumps = [0] * 9
        for i in range(9):
            bumps[i] = abs(list_heights[i] - list_heights[i + 1])
        bump = 0
        for i in range(9):
            bump += bumps[i]
        return bump


def score_calc(board, possibility, possibility2=None):
    #print(aggregate_height(board, possibility), complete_lines(board, possibility), holes_count(board, possibility), bumpiness(board, possibility))
    if possibility2 is None:
        score = agg_weight * aggregate_height(board, possibility)
        score += complete_weight * complete_lines(board, possibility)
        score += holes_weight * holes_count(board, possibility)
        score += bump_weight * bumpiness(board, possibility)
        return score
    else:
        score = agg_weight * aggregate_height(board, possibility, possibility2)
        score += complete_weight * complete_lines(board, possibility, possibility2)
        score += holes_weight * holes_count(board, possibility, possibility2)
        score += bump_weight * bumpiness(board, possibility, possibility2)
        return score


def collisions_underneath(board, possibility, possibility2=None):
    if possibility2 is None:
        for j in range(4):
            if (possibility[j][0], possibility[j][1] - 1) in board.cells:
                return False
        return True
    else:
        for j in range(4):
            if (possibility2[j][0], possibility2[j][1] - 1) in board.cells or (possibility2[j][0], possibility2[j][1] - 1) in possibility:
                return False
        return True

def row_by_row_solver(board):
    # max_height = get_max_height(board)
    possibilities_list = []
    possibilities_list_2 = []
    rotations_list = []
    rotations_list_2 = []
    scores = []
    for row in range(23, 0, -1):
        for column in range(10):
            # not occupied check
            if (column, row) not in board.cells:
                possibilities, rotation = rotation_coords_list(board, (column, row))
                for i in range(len(possibilities)):
                    # out of bounds check
                    if check_for_out_of_bounds(possibilities[i]) and collision_check(possibilities[i], board):
                        if collisions_underneath(board, possibilities[i]):
                            score1 = score_calc(board, possibilities[i])
                            possibilities_list.append(possibilities[i])
                            rotations_list.append(rotation[i])
                            scores.append(score1)
    max_score = 0
    for i in range(1, len(scores)):
        if scores[i] > scores[max_score]:
            max_score = i
    return possibilities_list[max_score], rotations_list[max_score]


class Player:
    def __init__(self):
        self.row_by_row = 0
        self.possibility2 = [(0, 0)] * 4
        self.rotation2 = -1

    def choose_action(self, board):
        #print(DEFAULT_SEED)
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


class RandomPlayer(Player):
    def __init__(self, seed=None):
        self.random = Random(seed)

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
        # self.print_board(board)
        lists = []
        # time.sleep(0.5)
        lists.append(row_by_row_solver(board))
        print(lists)
        if self.random.random() > 0.97:
            # 3% chance we'll discard or drop a bomb
            return self.random.choice([
                Action.Discard,
                # Action.Bomb,
            ])
        else:
            # 97% chance we'll make a normal move
            return self.random.choice([
                Direction.Left,
                Direction.Right,
                Direction.Down,
                Rotation.Anticlockwise,
                Rotation.Clockwise,
            ])


SelectedPlayer = Player

"""
                            for column_2 in range(10):
                                # not occupied check 2
                                if (column_2, row) not in board.cells and (column_2, row) not in possibilities[i]:
                                    possibilities_2, rotation_2 = rotation_coords_list(board, (column_2, row))
                                    for j in range(len(possibilities_2)):
                                        # out of bounds check 2
                                        if check_for_out_of_bounds(possibilities[i], possibilities_2[j]):
                                            if collision_check(possibilities[i], board, possibilities_2[j]):
                                                if collisions_underneath(board, possibilities[i], possibilities_2[j]):
                                                    score2 = score_calc(board, possibilities[i], possibilities_2[j])
                                                    possibilities_list.append(possibilities[i])
                                                    rotations_list.append(rotation[i])
                                                    possibilities_list_2.append(possibilities_2[j])
                                                    rotations_list_2.append(rotation_2[j])
                                                    scores.append(score1 + score2)
                                                    print(scores)
    def choose_action(self, board):
        #print(DEFAULT_SEED)
        print("started")
        if self.row_by_row == 0:
            print("good")
            possibility, rotation, self.possibility2, self.rotation2 = row_by_row_solver(board)
            print(possibility, rotation, self.possibility2, self.rotation2)
            self.row_by_row = 1
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
        if self.row_by_row == 1:
            self.row_by_row = 0
            if self.rotation2 < 0:
                yield Rotation.Anticlockwise
            else:
                for rotate in range(self.rotation2):
                    yield Rotation.Clockwise
            current_pos = list(sorted(board.falling.cells))[0]
            end_pos = sorted(self.possibility2)[0]
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
"""
