from tracemalloc import stop
from pysat.solvers import Glucose3
from math import log, ceil

N = 5
size = N**2
clauses = [] # for debugging
current = size + 1

# def location_to_index_offset(i, j, k):
#     return (i-1)*k + (j-1)

def EK(list, k):
    global current
    n = len(list)
    R = [[current + i*k + j for j in range(k)] for i in range(n)]
    current += N*k

    clauses = generate_clauses(list, k, R)
    # print(clauses)
    AMK_clauses = AMK(list, k, R)
    ALK_clauses = ALK(list, k, R)
    clauses += AMK_clauses
    clauses += ALK_clauses
    return clauses


def generate_clauses(list, k, R):
    global current
    clauses = []
    n = len(list)


    # print("additional_var_board: ", additional_var_board)
    # upto n-1 which mean from 0 to n-2
    for i in range(n - 1):
        clause = [-list[i], R[i][0]]
        clauses.append(clause)

    for i in range(1, n - 1):
        for j in range(min(i-1, k-1) + 1):
            clause = [-R[i-1][j], R[i][j]]
            clauses.append(clause)
            clause = [list[i], R[i-1][j], -R[i][j]]
            clauses.append(clause)
        
    for i in range(1, n-1):
        for j in range(1, min(i, k-1) + 1):
            clause = [-list[i], -R[i-1][j-1], R[i][j]]
            clauses.append(clause)
            clause = [R[i-1][j-1], -R[i][j]]
            clauses.append(clause)

    for i in range(k):
        clause = [list[i], -R[i][i]]
        clauses.append(clause)

    # print("clauses: ", clauses)
    return clauses

# generate_clauses([1, 2, 3, 4, 5], 3)

def AMK(list, k, R):
    clauses = []
    n = len(list)
    for i in range(k, n):
        clause = [-list[i], -R[i-1][k-1]] # might have a problem here idk lol
        clauses.append(clause)
    return clauses

def ALK(list, k, R):
    clauses = []
    n = len(list)
    clauses.append([R[n-2][k-1], list[n-1]])
    clauses.append([R[n-2][k-1], R[n-2][k-2]])
    return clauses

# EK([1, 2, 3, 4, 5], 3)
def main():
    with Glucose3() as g: 

        rows = []
        for y in range(N):
            row = []
            for x in range(N):
                row.append(y*N + x + 1)
            rows.append(row)
            g.add_clause(row)

        for row in rows:
            seq_clauses = EK(row, 1)
            for clause in seq_clauses:
                g.add_clause(clause)

        cols = []
        for x in range(N):
            col = []
            for y in range(N):
                col.append(x + y*N + 1)
            cols.append(col)
            g.add_clause(col)

        for col in cols:
            seq_clauses = EK(col, 1)
            for clause in seq_clauses:
                g.add_clause(clause)

        k_plus = {}
        k_minus = {}
        
        for y in range(N):
            for x in range(N):
                val = (x + y*N + 1)
                if y-x not in k_minus.keys():
                    k_minus[y-x] = [val]
                else:
                    k_minus[y-x].append(val)
                if y+x not in k_plus.keys():
                    k_plus[y+x] = [val]
                else:
                    k_plus[y+x].append(val)

        filtered_k_plus = {k:v for k, v in k_plus.items() if len(v) > 1}
        filtered_k_minus = {k:v for k, v in k_minus.items() if len(v) > 1}

        for diag in filtered_k_plus.values():
            seq_clauses = EK(diag, 1)
            for clause in seq_clauses:
                g.add_clause(clause)
        
        for diag in filtered_k_minus.values():
            seq_clauses = EK(diag, 1)
            for clause in seq_clauses:
                g.add_clause(clause)

        # for diag in filtered_k_minus.values():
        #     seq_clauses = generate_seq_clauses(diag)
        #     for clause in seq_clauses:
        #         g.add_clause(clause)

        print("clauses are: ", clauses)
        if g.solve():
            print("satisfiable")
            print("Model: ", g.get_model()[:size])
            print_board(g.get_model()[:size], N)
        else:
            print("unsatisfiable")


def print_board(board, size):
    for y in range(size):
        for x in range(size):
            if (y*size + x < len(board)):
                print('.' if board[y*size + x] < 0 else 'Q', end=' ')
        print()

if __name__ == "__main__":
    main()


# [1, 2, 3, 4]
# => [-1, 5] n (2 v 5) -> 6 => -(2 v 5) v 6 => (-2 n -5) v 6
# => n [-2, 6] n [-5, 6]
# n [-5, -2] n ... n [-7, -4]
def generate_seq_clauses(list):
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