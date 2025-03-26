from pysat.solvers import Glucose3
import time

num_weeks = 11
players_per_group = 3
num_groups = 9
num_players = players_per_group * num_groups
initial_var_count = num_weeks * num_groups * num_players
current = initial_var_count + 1

def get_variable(player, week, group):
    player -= 1
    group -= 1
    week -= 1
    return (player * num_groups * num_weeks) + (week * num_groups) + group + 1

def get_all_clauses():
    clauses = []
    clauses += ensure_golfer_plays_exactly_once_per_week()
    clauses += ensure_group_contains_exactly_p_players()
    clauses += ensure_no_repeated_players_in_group()
    # print(clauses)
    return clauses

def ensure_golfer_plays_exactly_once_per_week():
    clauses = []
    for player in range(1, num_players + 1):
        for week in range(1, num_weeks + 1):
            list = []
            for group in range(1, num_groups + 1):
                list.append(get_variable(player, week, group))
            clauses += EO(list)
    return clauses

def ensure_group_contains_exactly_p_players():
    clauses = []
    for week in range(1, num_weeks + 1):
        for group in range(1, num_groups + 1):
            list = []
            for player in range(1, num_players + 1):
                list.append(get_variable(player, week, group))
            clauses += EK(list, players_per_group)
    return clauses

def ensure_no_repeated_players_in_group():
    clauses = []

    for week in range(1, num_weeks + 1):
        for group in range(1, num_groups + 1):
            for player in range(1, num_players + 1):
                for other_player in range(player + 1, num_players + 1):
                    for other_group in range(1, num_groups + 1):
                        for other_week in range(week + 1, num_weeks + 1):
                            clauses.append([
                                -get_variable(player, week, group),
                                -get_variable(other_player, week, group),
                                -get_variable(player, other_week, other_group),
                                -get_variable(other_player, other_week, other_group)
                            ])
    return clauses

def EO(list):
    clauses = []
    ALO = []
    for i in list:
        ALO.append(i)
    clauses.append(ALO)
    AMO = generate_AMO_clauses(list)
    clauses += AMO
    return clauses

# EO([1, 2, 3, 4])

def generate_AMO_clauses(list):
    global current
    clauses = []
    for idx, x in enumerate(list):
        if idx == 0:
            clauses.append([-x, current])
            current += 1
        elif idx == len(list) - 1:
            clauses.append([-x, -current+1])
            current += 1
        else:
            clauses.append([-x, current])
            clauses.append([-current+1, current])
            clauses.append([-x, -current+1])
            current += 1
    return clauses

# exactly k is a combination of clause 1 to 6 and clause 7 and 8
def EK(list, k):
    global current
    list = [0] + list
    n = len(list) - 1
    R = generate_R(k, n, current)
    # print(R)
    current += n*k

    clauses = []
    clauses += generate_clauses(list, k, R, n)
    # print(clauses)
    clause_8 = generate_clause_8(list, k, R, n)
    clause_7 = generate_clause_7(list, k, R, n)
    clauses += clause_8
    clauses += clause_7
    return clauses

# clause 1 to 6 and clause 7
def ALK(list, k):
    global current
    list = [0] + list
    n = len(list) - 1
    R = generate_R(k, n, current)
    current += n*k

    clauses = []
    clauses += generate_clauses(list, k, R, n)
    return clauses

# clause 1 to 6 and clause 8
def AMK(list, k):
    global current
    list = [0] + list
    n = len(list) - 1
    R = generate_R(k, n, current)
    current += n*k

    clauses = []
    clauses += generate_clauses(list, k, R, n)
    AMK_clauses = generate_clause_8(list, k, R, n)
    clauses += AMK_clauses
    return clauses

def generate_R(k, n, current):
    R = [[current + i*k + j for j in range(k)] for i in range(n)]
    # add padding 0s to the R matrix for easier 1-indexing
    R = [[0 for _ in range(k)]] + R
    R = [[0] + i for i in R]
    return R

# generates clauses 1 to 6
def generate_clauses(list, k, R, n):
    clauses = []
    # n = len(list) - 1

    # formula (1)
    for i in range(1, n):
        clause = [-list[i], R[i][1]]
        clauses.append(clause)

    # formula (2), (4)
    for i in range(2, n):
        for j in range(1, min(i-1, k) + 1):
            clause = [-R[i-1][j], R[i][j]]
            clauses.append(clause)
            clause = [list[i], R[i-1][j], -R[i][j]]
            clauses.append(clause)
    # print(clause)
        
    # formula (3), (6)
    for i in range(2, n):
        for j in range(2, min(i, k) + 1):
            clause = [-list[i], -R[i-1][j-1], R[i][j]]
            clauses.append(clause)
            clause = [R[i-1][j-1], -R[i][j]]
            clauses.append(clause)

    # formula (5)
    for i in range(1, k+1):
        clause = [list[i], -R[i][i]]
        clauses.append(clause)

    # print("clauses: ", clauses)
    return clauses

def generate_clause_8(list, k, R, n):
    clauses = []
    for i in range(k+1, n+1):
        clause = [-list[i], -R[i-1][k]]
        clauses.append(clause)
    return clauses

def generate_clause_7(list, k, R, n):
    clauses = []
    if k == 1:
        return clauses
    clauses.append([R[n-1][k], list[n]])
    clauses.append([R[n-1][k], R[n-1][k-1]])
    return clauses

# print(EK([1, 2, 3, 4, 5], 2))

def main():
    with Glucose3() as g: 
        start_time = time.time()
        clauses = get_all_clauses()
        for clause in clauses:
            g.add_clause(clause)

        if g.solve():
            print("satisfiable")
            print("Model: ", g.get_model())
            # print_board(g.get_model()[:size], N)
        else:
            print(g.solve_limited(expect_interrupt=True))
            print(g.nof_clauses(), g.nof_vars())
            print("unsatisfiable")
        
        end_time = time.time()
        print("Time taken: ", end_time - start_time)


def print_board(board, size):
    for y in range(size):
        for x in range(size):
            if (y*size + x < len(board)):
                print('.' if board[y*size + x] < 0 else 'Q', end=' ')
        print()

if __name__ == "__main__":
    main()