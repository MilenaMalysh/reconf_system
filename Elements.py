import copy
from collections import OrderedDict
import itertools
from sympy.parsing.sympy_parser import parse_expr
from sympy import *

processors = {"pr1": {"nom": 40, "max": 100, "actual": 0, "variants": [{"pr2": 40}, {"pr5": 40}]},
              "pr2": {"nom": 70, "max": 110, "actual": 0, "variants": [{"pr1": 50, "pr5": 10}, {"pr1": 50, "pr6": 10}]},
              "pr5": {"nom": 30, "max": 70, "actual": 0, "variants": [{"pr1": 30}, {"pr2": 30}]},
              "pr6": {"nom": 60, "max": 70, "actual": 0, "variants": [{"pr1": 60}, {"pr2": 40, "pr5": 20}]}}


class Elements:
    def __init__(self):
        d1, d2, d3, d5, d6, d7, c1, c2, c3, c4, c5, m1, m2, b2, b4, b5, a1, a3, pr1, pr2, pr5, pr6 = symbols(
            'd1, d2, d3, d5, d6, d7, c1, c2, c3, c4, c5, m1, m2, b2, b4, b5, a1, a3, pr1, pr2, pr5, pr6')
        self.elements = {"d1": True, "d2": True, "d3": True, "d5": True, "d6": True, "d7": True, "c1": True, "c2": True,
                         "c3": True, "c4": True, "c5": True, "m1": True, "m2": True, "b2": True, "b4": True, "b5": True,
                         "a1": True, "a3": True, "pr1": True, "pr2": True, "pr5": True, "pr6": True}
        self.faults_statistic = {"d1": 0, "d2": 0, "d3": 0, "d5": 0, "d6": 0, "d7": 0, "c1": 0, "c2": 0, "c3": 0,
                                 "c4": 0, "c5": 0, "m1": 0, "m2": 0, "b2": 0, "b4": 0, "b5": 0, "a1": 0, "a3": 0,
                                 "pr1": 0, "pr2": 0, "pr5": 0, "pr6": 0}
        self.formula = parse_expr(
            "And(d1, d2, c1, b2, d3, c2, Or(pr1, pr2, And(a1, m2, a3, Or(b4, b5), pr6)), d5, c3, pr5, d6, d7, c4, c5, b4, m1, a1, a3, m2, Or(pr6, And(b2, Or(pr1, pr2))))"

            )
        self.formula_optimized = parse_expr(
            "And(d1, d2, Or(c1,c2), b2, Or(pr1, pr2, And(a1, m2, a3, Or(b4, b5), pr6)), d3, d5, Or(c2, c3), pr5, d6, d7, Or(And(c4, m1, a1, Or(And(m2, a3, pr6, Or(b4, b5)), And(b2, Or(pr2, pr1)))) ,And(c5, b4, pr6)))"
        )
        self.vectors = [list(itertools.combinations(self.elements.keys(), 3)),
                        list(itertools.combinations(self.elements.keys(), 4))]
        self.tolerances = {"p": 0.000012, "a": 0.00032, "c": 0.00007, "d": 0.000032, "b": 0.000034, "m": 0.00033}
        self.probability = -1000000000

    def generate_vector(self, combination):
        self.set_true()
        for k in combination:
            self.elements[k] = False
        self.probability = self.calculate_probability()
        return self.is_faulted()

    def generate_vector_by_index(self, number, faults):
        self.set_true()
        for k in self.vectors[faults - 3][number]:
            self.elements[k] = False
        self.vectors[faults - 3].pop(number)
        self.probability = self.calculate_probability()
        return self.is_faulted()

    def set_true(self):
        for k, v in self.elements.items():
            self.elements[k] = True

    def is_faulted(self):
        nulled_processors_dict = {k: v for (k, v) in self.elements.items() if
                                  (k in ['pr1', 'pr2', 'pr5', 'pr6']) and not v}
        old_elements = copy.deepcopy(self.elements)

        if nulled_processors_dict:
            self.load_transfer(nulled_processors_dict)

        faulted = self.formula.subs(list(self.elements.items()))
        if not faulted:
            for k, v in old_elements.items():
                if not v:
                    self.faults_statistic[k] += 1
        return faulted

    def calculate_probability(self):
        probability = 1
        for k, v in self.elements.items():
            particular_probability = 1 - self.tolerances.get(k[0]) if v else self.tolerances.get(k[0])
            probability *= particular_probability
        return probability

    def load_transfer(self, nulled):
        proc = copy.deepcopy(processors)
        recovered = []
        for k in proc:
            if k in nulled:
                proc[k]["actual"] = proc[k]["max"]
            else:
                proc[k]["actual"] = proc[k]["nom"]
        for k in nulled:
            disabled = proc[k]
            for v in disabled["variants"]:
                success = True
                for pr, est_power in v.items():
                    if est_power + proc[pr]["actual"] > proc[pr]["max"]:
                        success = False
                if success:
                    for pr, est_power in v.items():
                        proc[pr]["actual"] += est_power
                    recovered.append(k)
                    break
        for pr in recovered:
            self.elements[pr] = True
