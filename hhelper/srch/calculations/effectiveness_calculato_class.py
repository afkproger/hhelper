
import itertools
import numpy as np
from sympy import symbols, Eq, solve, ccode
from math import inf


class EffectivenessCalculator:

    def __init__(self, survey_results):
        self.__survey_results = survey_results
        self.__count_indicators = len(survey_results)
        self.__lst_parameters = []

    def get_parameters_list(self):
        lst_parameters = []
        count_indicators = len(self.__survey_results)
        combinations = self.__generate_combinations()
        paired_indicators = self.__create_paired_combinations(combinations)
        sugeno_measure = self.find_sugeno_measure(self.get_value_of_survey_results())
        print(sugeno_measure)
        self.create_survey(combinations, sugeno_measure)
        for x in combinations:
            print(x)
        lst_parameters.append(self.__calculation_f_extreme(combinations))
        for i in range(count_indicators):
            lst_parameters.append(self.__calculation_f_n(combinations, i))

        lst_parameters += self.__calculation_paired_coeff(combinations, paired_indicators)
        # lst_parameters.append(self.__calculation_f_extreme(combinations, is_last=True))
        #
        self.__lst_parameters = [float(x) for x in lst_parameters]

        return self.__lst_parameters

    def __generate_combinations(self):
        return [list(combo) for combo in itertools.product([-1, 1], repeat=self.__count_indicators)]

    # расчитываем значения парного произведения показатлей после опроса
    def __calculate_paired_indicators(self, data, n):
        # # Находим все возможные уникальные комбинации пар индексов для показателей

        all_combinations = []

        # Проходим по длинам от 2 до n (например, для f1, f2, ..., fn)
        for r in range(2, n + 1):
            # Генерируем все возможные комбинации индексов длины r
            combinations = list(itertools.combinations(range(n), r))

            # Для каждой комбинации вычисляем произведение соответствующих столбцов
            combo_result = np.column_stack([np.prod(data[:, comb], axis=1) for comb in combinations])

            # Добавляем результат в общий список
            all_combinations.append(combo_result)

        # Объединяем все комбинации в одну матрицу по горизонтали
        result_matrix = np.hstack(all_combinations)

        return result_matrix

    # создаём часть матрицы для парного произведения показателей после опроса
    def __create_paired_combinations(self, combinations):
        data = np.array(combinations)
        result = self.__calculate_paired_indicators(data, len(combinations[0]))
        return result

    def __generate_expression(self, coefficients, variable):
        # Генерация произведения вида (1 + coeff * lambda_) для каждого коэффициента
        expression = 1
        for coeff in coefficients:
            expression *= (1 + coeff * variable)

        return expression

    def find_sugeno_measure(self, coefficients, lambda_value=None):
        lambda_ = symbols('lambda')
        expression = self.__generate_expression(coefficients, lambda_)
        numerator = expression - 1
        if lambda_value is None:
            equation = Eq(numerator / lambda_, 1)

            # Решаем уравнение
            solutions = solve(equation, lambda_)
            for solution in solutions:
                if -1 < solution < inf:
                    return solution
        else:
            result = numerator.subs(lambda_, lambda_value) / lambda_value
            return result

    # функция для вычленения экспертных оценок в простых опорных ситуациях
    def get_value_of_survey_results(self):
        lst = [self.__survey_results.get(x) for x in self.__survey_results.keys()]
        return lst

    # добавляем в матрицу опроса значения экспертов
    def __processing_simple_rules(self, combinations):
        simple_rules = [comb for comb in combinations if
                        sum(comb) == -(self.__count_indicators - 2)]  # выбрали опорные ситуации из выборки
        for comb in simple_rules:
            for i in range(0, len(comb)):
                if comb[i] == 1:
                    comb.append(self.__survey_results[i])

    # функция для расчёта показателя в сложных опорных ситуациях
    def __estimate_resulting_indicator(self, comb, sugeno_measure):
        coeff_lst = []  # список коэффицентов для сложных правил
        for i in range(0, len(comb)):
            if comb[i] == 1:
                coeff_lst.append(self.__survey_results[i])
        comb.append(round(self.find_sugeno_measure(coeff_lst, sugeno_measure), 6))

    # функция после которой в базовую матрицу опроса добавлены оценки экспертов
    # для в простых опорных ситуациях, расчитаны и добавлены оценкци в сложных
    # опорных ситуациях
    def create_survey(self, combinations, sugeno_measure):
        self.__processing_simple_rules(combinations)
        combinations[0].append(0)
        combinations[-1].append(1)
        for comb in combinations:
            if len(comb) == self.__count_indicators:
                self.__estimate_resulting_indicator(comb, sugeno_measure)

    def __calculation_f_extreme(self, combinations, is_last=None):
        if is_last is None:

            sum_ = 0
            count_comb = len(combinations)

            for i in range(count_comb):
                sum_ += combinations[i][-1]

            copy_result = sum_ / count_comb
            result = round(copy_result, 6)
            if result != 0:
                result = '{:6g}'.format(result)
                return result
            else:
                return copy_result
        else:
            # в этот момент у нас в combo уже хранится расчитанные значения в опорных ситуациях
            last_indicators = [[np.prod(combo[:-1])] for combo in combinations]
            sum_ = 0
            count_comb = len(last_indicators)
            for i in range(count_comb):
                sum_ += (last_indicators[i][0] * combinations[i][-1])
            copy_result = sum_ / count_comb
            result = round(copy_result, 6)
            if result != 0:
                result = '{:6g}'.format(result)
                return result
            else:
                return copy_result

    def __calculation_f_n(self, combination, index, is_paired_indicators=None):
        result = 0
        count_comb = len(is_paired_indicators) if is_paired_indicators is not None else len(combination)

        # Вычисление результата
        if is_paired_indicators is None:
            for i in range(count_comb):
                result += (combination[i][index] * combination[i][-1])
        else:
            for i in range(count_comb):
                result += is_paired_indicators[i][index] * combination[i][-1]

        # Среднее значение
        copy_result = result / count_comb
        result = round(copy_result, 6)

        # Форматирование результата
        if result != 0:
            return '{:6g}'.format(result)
        else:
            return copy_result

    def __calculation_paired_coeff(self, combinations, paired_combinations):
        indicators = []
        for i in range(len(paired_combinations[0])):
            indicators.append(self.__calculation_f_n(combinations, i, is_paired_indicators=paired_combinations))
        return indicators

    # функция формирующая массив типа ['f1', 'f2', 'f3' , 'fn'] для работы комплекса
    def __get_fn_combinations(self):
        # Получаем количество показателей на основе ключей словаря
        count_factors = self.__count_indicators

        # Формируем список строк 'f1', 'f2', ..., 'fn'
        fn_labels = [f"f{i + 1}" for i in range(count_factors)]

        # Создаем комбинации от одиночных 'f1', 'f2', ..., до 'f1f2', 'f1f2f3', и т.д.
        all_combinations = []
        for r in range(1, count_factors + 1):
            combinations = itertools.combinations(fn_labels, r)
            for combo in combinations:
                all_combinations.append(''.join(combo))

        return all_combinations

    def get_formula(self):
        fn_labels = self.__get_fn_combinations()
        fn_labels.insert(0, 'f0')
        return self.__generate_formula(fn_labels)

    import itertools

    # сформируем пока для проверки свёотки словарь вида fn - арг
    def __generate_formula(self, factors):
        formula = dict()
        for i in range(len(self.__lst_parameters)):
            formula[factors[i]] = self.__lst_parameters[i]

        return formula
