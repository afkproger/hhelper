from itertools import combinations

class Score:
    @classmethod
    def get_score(cls , variables):
        param_list = [0.54862, 0.077398, 0.258212, 0.163009, -0.013009, -0.008212, -0.027398, 0.00138]
        # fn_labels = ['*j1', '*j2', '*j3', '*j1*j2', '*j1*j3', '*j2*j3', '*j1*j2*j3']
        return cls.calculate_polynomial(param_list , variables)

    @classmethod
    def calculate_polynomial(cls,coefficients, variables):
        n = len(variables)
        j_result = coefficients[0]  # Свободный член

        # Проходим по коэффициентам и переменным (от одиночных до шестимерных взаимодействий)
        index = 1
        for k in range(1, n + 1):
            for comb in combinations(range(n), k):
                prod = 1
                for i in comb:
                    prod *= variables[i]
                j_result += coefficients[index] * prod
                index += 1

        return j_result