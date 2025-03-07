# Author: Rishabh Singh
import math
from ortools.linear_solver import pywraplp

def ticket_score_func(attribute_list, attribute_prop_dict, attribute_vuln_dict):
    quasi_list = ['zip code', 'job', 'company', 'cc provider']
    quasi_attribute_present = []
    for attribute in attribute_list:
        for quasi_attribute in quasi_list:
            if attribute == quasi_attribute:
                quasi_attribute_present.append(attribute)
                attribute_list.remove(attribute)

    score_1 = 0
    score_2 = 0
    for attribute in attribute_list:
        score_1 = score_1 + attribute_prop_dict[attribute] * attribute_vuln_dict[attribute]

    quasi_dimension = len(quasi_attribute_present)
    if quasi_dimension > 0:
        for attribute in quasi_attribute_present:
            score_2 = score_2 + attribute_prop_dict[attribute] * attribute_vuln_dict[attribute]

    score_2 = ((math.e / 2) ** math.log(quasi_dimension)) * score_2
    ticket_score = score_1 + score_2

    return ticket_score, score_1, score_2

def disclosure_proportion(atrributes_vul_1, atrributes_vul_2, atrributes_vul_3, atrributes_vul_4, atrributes_vul_5, pf):
    solver = pywraplp.Solver.CreateSolver('SCIP')

    variables_list = ['very high', 'high', 'medium', 'low', 'very low']
    vul_list = [5,4,3,2,1]

    # model variables
    x = {}

    for variable in variables_list:
        x[variable] = solver.NumVar(0, 1, 'x')

    # constraints

    quasi_dimension = len(atrributes_vul_2) + len(atrributes_vul_3)

    coef_1 = len(atrributes_vul_1)*1
    coef_4 = len(atrributes_vul_4)*4
    coef_5 = len(atrributes_vul_5)*5

    coef_2 = ((math.e / 2) ** math.log(quasi_dimension)) * (len(atrributes_vul_2)*2)
    coef_3 = ((math.e / 2) ** math.log(quasi_dimension)) * (len(atrributes_vul_3)*3)

    solver.Add(coef_5 * x['very high'] + coef_4 * x['high'] + coef_3 * x['medium'] + coef_2 * x['low'] + coef_1 * x['very low'] <=
               (1 - pf) * (coef_5 + coef_4 + coef_3 + coef_2))
    
    for i in range(4):
        solver.Add((1+vul_list[i]/sum(vul_list))*x[variables_list[i]] <= (1+vul_list[i+1]/sum(vul_list))*x[variables_list[i+1]])

    solver.Maximize(x['very high'] + x['high'] + x['medium'] + x['low'] + x['very low'])
    status = solver.Solve()
    if status == pywraplp.Solver.OPTIMAL or status == pywraplp.Solver.FEASIBLE:
        x_copy = {}
        for variable in variables_list:
            x_copy[variable] = round(x[variable].solution_value(), 2)
        return x_copy
    else:
        return 0