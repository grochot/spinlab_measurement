import json 

def fit_parameters_to_file(fit_parameters, file_name="fit_parameters.json"):
    dict_to_save = {}
    for i, fit_parameter in enumerate(fit_parameters):
        dict_to_save["param_{}".format(i)] = fit_parameter
    with open(file_name, 'w') as f:
        json.dump(dict_to_save, f)

def fit_parameters_from_file(file_name="fit_parameters.json"):
    with open(file_name, 'r') as f:
        fit_parameters = json.load(f)
    list_parameters = list(fit_parameters.values())
    print(list_parameters)
    return list_parameters