import pysat
from pysat.solvers import Glucose3
import pysat.examples

N = 100

clauses = []

with Glucose3() as g:
    
    # (1v2v3v4) n (5v6v7v8) n (9v10v11v12) n (13v14v15v16)
    for y in range(N):
        at_least_one_clause = []
        for x in range(N):
            at_least_one_clause.append(y*N + x + 1)
            for x_running in range(x+1, N):
                clause = [-(y*N + x+1), -(y*N + x_running+1)]
                clauses.append(clause)
                g.add_clause(clause)
        clauses.append(at_least_one_clause)
        g.add_clause(at_least_one_clause)

    for x in range(N):
        at_least_one_clause = []
        for y in range(N):
            at_least_one_clause.append(x + y*N + 1)
            for y_running in range(y+1, N):    
                clause = [-(x + y*N +1), -(x + y_running*N +1)]
                clauses.append(clause)
                g.add_clause(clause)
        clauses.append(at_least_one_clause)
        g.add_clause(at_least_one_clause)

    k_plus = {}
    k_minus = {}

    for y in range(N):
        for x in range(N):
            val = -(x + y*N + 1)
            if y-x not in k_minus.keys():
                k_minus[y-x] = [val]
            else:
                k_minus[y-x].append(val)
            if y+x not in k_plus.keys():
                k_plus[y+x] = [val]
            else:
                k_plus[y+x].append(val)


    # print("K minuss is: ", k_minus)
    # print("k plus is", k_plus)
    for diag in k_plus.values():
        if len(diag) > 1:
            for i in range(len(diag)):
                for j in range(i+1, len(diag)):
                    g.add_clause([diag[i], diag[j]])
                    clauses.append([diag[i], diag[j]])

    for diag in k_minus.values():
        if len(diag) > 1:
            for i in range(len(diag)):
                for j in range(i+1, len(diag)):
                    g.add_clause([diag[i], diag[j]])
                    clauses.append([diag[i], diag[j]])
                    
    if g.solve():
        print("satisfiable")
        print("Model: ", g.get_model())
        print("N^2 = ", N**2)
        print("Clauses size is: ", len(clauses))
    else:
        print("unsatisfiable")
