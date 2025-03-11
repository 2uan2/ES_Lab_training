from pysat.solvers import Glucose3
from math import log, ceil, sqrt


N = 4
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
            seq_clauses = generate_clauses(row)
            for clause in seq_clauses:
                # clauses.append(clause)
                g.add_clause(clause)

        cols = []
        for x in range(N):
            col = []
            for y in range(N):
                col.append(x + y*N + 1)
            cols.append(col)
            g.add_clause(col)

        for col in cols:
            seq_clauses = generate_clauses(col)
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

        print("filtered k plus is: ", filtered_k_plus.values())

        for diag in filtered_k_plus.values():
            seq_clauses = generate_clauses(diag)
            for clause in seq_clauses:
                clauses.append(clause)
                g.add_clause(clause)

        for diag in filtered_k_minus.values():
            seq_clauses = generate_clauses(diag)
            for clause in seq_clauses:
                g.add_clause(clause)

        print("clauses are: ", clauses)
        if g.solve():
            print("satisfiable")
            print("Model: ", g.get_model()[:size])
            print_board(g.get_model()[:size], N)
        else:
            print("unsatisfiable")


# [6, 7, 8, 9, 10]
# commander count = ceil(sqrt(n)) = 3
# commanders = [11, 12, 13]
# c1 -> EO([11, 12, 13])
def generate_clauses(arr):
    global current
    clauses = []
    
    if len(arr) <= 3:
        return generate_binomial_clauses(arr)

    commander_count = ceil(sqrt(len(arr)))
    commanders = []
    member_count = ceil(len(arr) / commander_count)
    # print(commander_count)
    # print(member_count)
    for i in range(commander_count):
        commander = current
        current += 1
        commanders.append(commander)
        member = []
        for j in range(member_count):
            if i*member_count+j >= len(arr):
                break
            # print(i*commander_count+j)
            member.append(arr[i*member_count+j])
        # print(member)
        
        
        no_commander_clauses = [[commander, -x] for x in member]
        for clause in no_commander_clauses:
            # print(clause)
            clauses.append(clause)
        # print(no_commander_clauses)

        if len(member) > 1:
            # print("members are: ", member)
            member_pairs = generate_binomial_clauses(member)
            # print("members are: ", member)
            for pair in member_pairs:
                # pair.append(-commander)
                clauses.append(pair)
            member.append(-commander)
            clauses.append(member)

    # print(commanders)
    if len(commanders) > 1:
        clauses.append(commanders)
    at_most_one_commander = generate_binomial_clauses(commanders)
    for clause in at_most_one_commander:
        clauses.append(clause)


    return clauses

# [5, 6, 7, 8]
# => [-5, -6] n [-5, -7] n [-5, -8] n [-6, -7] n [-6, -8] n [-7, -8]
def generate_binomial_clauses(arr):
    clauses = []
    for i, x in enumerate(arr):
        # if len(arr) == 1:
        for j, x_running in enumerate(arr[i+1:]):
            clauses.append([-(x), -(x_running)])
    # print(clauses)
    return clauses


def print_board(board, size):
    for y in range(size):
        for x in range(size):
            if (y*size + x < len(board)):
                print('.' if board[y*size + x] < 0 else 'Q', end=' ')
        print()

if __name__ == "__main__":
    main()
    # print(generate_binomial_clauses([1, 2, 6, 4]))
    # print(generate_clauses([1, 2, 3, 4, 5, 6, 7, 8, 9, 10]))