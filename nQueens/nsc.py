from pysat.solvers import Glucose3

N = 20
size = N**2
current = size + 1

# exactly k is a combination of clause 1 to 6 and clause 7 and 8
def EK(list, k):
    global current
    list = [0] + list
    n = len(list) - 1
    R = generate_R(k, n, current)
    print(R)
    current += N*k

    clauses = []
    clauses += generate_clauses(list, k, R, n)
    # print(clauses)
    AMK_clauses = generate_clause_8(list, k, R, n)
    # print("AMK: ", AMK_clauses)
    ALK_clauses = generate_clause_7(list, k, R, n)
    # print("ALK: ", ALK_clauses)
    clauses += AMK_clauses
    clauses += ALK_clauses
    return clauses

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

# clause 1 to 6 and clause 7
def ALK(list, k):
    global current
    list = [0] + list
    n = len(list) - 1
    R = generate_R(k, n, current)
    current += N*k

    clauses = []
    clauses += generate_clauses(list, k, R, n)
    ALK_clauses = generate_clause_7(list, k, R, n)
    clauses += ALK_clauses
    return clauses

# clause 1 to 6 and clause 8
def AMK(list, k):
    global current
    list = [0] + list
    n = len(list) - 1
    R = generate_R(k, n, current)
    current += N*k

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
        # g.add_clause([2])

        # get all the rows that needs exactly one applied on
        rows = []
        for y in range(N):
            row = []
            for x in range(N):
                row.append(y*N + x + 1)
            rows.append(row)

        # apply exactly one on each row
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

        # dictionary of all the diagonals
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

        # filter out the diagonals that have less than 2 elements
        filtered_k_plus = {k:v for k, v in k_plus.items() if len(v) > 1}
        filtered_k_minus = {k:v for k, v in k_minus.items() if len(v) > 1}

        # apply at most one on the diagonals
        for diag in filtered_k_plus.values():
            seq_clauses = AMK(diag, 1)
            for clause in seq_clauses:
                g.add_clause(clause)
        
        for diag in filtered_k_minus.values():
            seq_clauses = AMK(diag, 1)
            for clause in seq_clauses:
                g.add_clause(clause)

        if g.solve():
            print("satisfiable")
            print("Model: ", g.get_model()[:size])
            print_board(g.get_model()[:size], N)
        else:
            print(g.solve_limited(expect_interrupt=True))
            print(g.nof_clauses(), g.nof_vars())
            print("unsatisfiable")


def print_board(board, size):
    for y in range(size):
        for x in range(size):
            if (y*size + x < len(board)):
                print('.' if board[y*size + x] < 0 else 'Q', end=' ')
        print()

if __name__ == "__main__":
    main()