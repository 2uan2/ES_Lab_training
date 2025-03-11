from pysat.solvers import Glucose3
from math import log, ceil


N = 5
size = N**2
clauses = []
current = size + 1
additional_size = N-1

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
            seq_clauses = generate_seq_clauses(row)
            for clause in seq_clauses:
                clauses.append(clause)
                g.add_clause(clause)

        cols = []
        for x in range(N):
            col = []
            for y in range(N):
                col.append(x + y*N + 1)
            cols.append(col)
            g.add_clause(col)

        for col in cols:
            seq_clauses = generate_seq_clauses(col)
            for clause in seq_clauses:
                # clauses.append(clause)
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
            seq_clauses = generate_seq_clauses(diag)
            for clause in seq_clauses:
                g.add_clause(clause)

        for diag in filtered_k_minus.values():
            seq_clauses = generate_seq_clauses(diag)
            for clause in seq_clauses:
                g.add_clause(clause)

        print("clauses are: ", clauses)
        if g.solve():
            print("satisfiable")
            print("Model: ", g.get_model()[:size])
            print_board(g.get_model()[:size], N)
        else:
            print("unsatisfiable")


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

def print_board(board, size):
    for y in range(size):
        for x in range(size):
            if (y*size + x < len(board)):
                print('.' if board[y*size + x] < 0 else 'Q', end=' ')
        print()

if __name__ == "__main__":
    main()