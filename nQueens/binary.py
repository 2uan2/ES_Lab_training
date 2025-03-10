from pysat.solvers import Glucose3
from math import log, ceil

def main():
    N = 20
    size = N**2
    # additional_var_count = ceil(log(size))
    clauses = []

    with Glucose3() as g: 

        current = size + 1
        additional_size = ceil(log(N, 2))

        rows = []
        for y in range(N):
            row = []
            for x in range(N):
                row.append(y*N + x + 1)
            rows.append(row)
            g.add_clause(row)

        for row in rows:
            binary_combinations = generate_binary_combinations(additional_size)
            # x = binary_combinations[i] = '00' 
            # => x -> -y1 n -y2 
            # => -x v (-y1 n -y2) 
            # => (-x v -y1) n (-x v -y2) 
            new_var = []
            for i in range(additional_size):
                new_var.append(i + current)
            current += additional_size
            for index, x in enumerate(row):
                for i, b in enumerate(binary_combinations[index]):
                    clause = [-x, new_var[i] if int(b) == 1 else -new_var[i]]
                    g.add_clause(clause)
                    # clauses.append(clause)


        cols = []
        for x in range(N):
            col = []
            for y in range(N):
                col.append(x + y*N + 1)
            cols.append(col)
            g.add_clause(col)

        for col in cols:
            binary_combinations = generate_binary_combinations(additional_size)
            new_var = []
            for i in range(additional_size):
                new_var.append(i + current)
            current += additional_size
            for index, x in enumerate(col):
                for i, b in enumerate(binary_combinations[index]):
                    clause = [-x, new_var[i] if int(b) == 1 else -new_var[i]]
                    g.add_clause(clause)
                    # clauses.append(clause)

        
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
                        
        
        for diag in filtered_k_minus.values():
            binary_combinations = generate_binary_combinations(additional_size)
            new_var = []
            for i in range(additional_size):
                new_var.append(i + current)
            current += additional_size
            for index, x in enumerate(diag):
                for i, b in enumerate(binary_combinations[index]):
                    clause = [-x, new_var[i] if int(b) == 1 else -new_var[i]]
                    g.add_clause(clause)
                    clauses.append(clause)

        for diag in filtered_k_plus.values():
            binary_combinations = generate_binary_combinations(additional_size)
            new_var = []
            for i in range(additional_size):
                new_var.append(i + current)
            current += additional_size
            for index, x in enumerate(diag):
                for i, b in enumerate(binary_combinations[index]):
                    clause = [-x, new_var[i] if int(b) == 1 else -new_var[i]]
                    g.add_clause(clause)
                    clauses.append(clause)
                        
        print("clauses are: ", clauses)
        if g.solve():
            print("satisfiable")
            print("Model: ", g.get_model()[:size])
            print_board(g.get_model()[:size], N)
            # print("N^2 = ", N**2)
            # print("Clauses size is: ", len(clauses))
        else:
            print("unsatisfiable")

def generate_binary_combinations(length):
    binary_combinations = []
    for i in range(2**length):
        binary_combinations.append(format(i, '0' + str(length) + 'b'))
    return binary_combinations

def print_board(board, size):
    # print(board)
    for y in range(size):
        for x in range(size):
            if (y*size + x < len(board)):
                print('.' if board[y*size + x] < 0 else 'Q', end=' ')
        print()

if __name__ == "__main__":
    main()