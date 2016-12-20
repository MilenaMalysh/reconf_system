import itertools
from sympy import *
from Elements import Elements
import random


def main():
    elements = Elements()
    fault_tolerance = 0
    random.seed()
    probability3 = 0
    probability4 = 0
    # calculation in case of 1, 2 faults
    for i in range(1, 3):
        for j in itertools.combinations(elements.elements.keys(), i):
            if not elements.generate_vector(j):
                fault_tolerance += elements.probability

    # calculation in case of 3 faults (combinations without repetition - 680)
    max_3faults = 1539
    for i in range(int(1540/2) + 1):
        rdm = random.randint(0, max_3faults - i)
        if not elements.generate_vector_by_index(rdm, 3):
            probability3 += elements.probability

    # calculation in case of 4 faults (combinations without repetition - 1428)
    max_4faults = 7314
    for i in range(int(max_4faults/10) + 1):
        rdm = random.randint(0, max_4faults - i)
        if not elements.generate_vector_by_index(rdm, 4):
            probability4 += elements.probability

    fault_tolerance += probability3 * 2
    fault_tolerance += probability4 * 10

    print("%.11f" % fault_tolerance)
    for i, k in sorted(elements.faults_statistic.items(), key = lambda x: x[1]):
        print(i, k)


if __name__ == "__main__":
    main()
