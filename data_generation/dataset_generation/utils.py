from typing import Any
from copy import deepcopy
from .processing_error import ProcessingError

def fill_template_params(template: str, params: dict) -> str:
    template = deepcopy(template)

    for param_name, param_value in params.items():
        template = template.replace("{"+param_name+"}", str(param_value))

    return template

def _check_strlen(x: str, full_out: any, min_len: int, max_len: int):
    if len(x) > max_len:
        raise ProcessingError("String length is too high", str(full_out))
    if len(x) < min_len:
        raise ProcessingError("String length is too low", str(full_out))

def check_if_type_is_correct(val: Any, params: dict) -> bool:
    required_type: str = params["output_type"]

    if required_type == "list[str]":
        min_len: int = params["min_len"]
        if not isinstance(val, list):
            raise ProcessingError("Value is not list", str(val))
        if not all(isinstance(o, str) for o in val):
            raise ProcessingError("Values of list are not str", str(val))
        if len(val) < min_len:
            raise ProcessingError("Minimum length not reached", str(val))
        for x in val:
            _check_strlen(x, val, params["min_strlen"], params["max_strlen"])
    
    elif required_type == "str":
        if not isinstance(val, str):
            raise ProcessingError("Values are not str", str(val))
        _check_strlen(val, val, params["min_strlen"], params["max_strlen"])
    
    elif required_type == "dict":
        if not isinstance(val, dict):
            raise ProcessingError("Value is not dict", str(val))

        parameters: list[str] = params["parameters"]

        # Check if all parameters are present
        for param_name, param_required_type in parameters:
            if param_name not in val:
                raise ProcessingError("Parameter not present", str(val))
            if param_required_type == "str":
                if not isinstance(val[param_name], str):
                    raise ProcessingError(f"Dict parameter {param_name} is not of required type", str(val))
                _check_strlen(val[param_name], val, params["min_strlen"], params["max_strlen"])

            elif param_required_type == "list[str]":
                if not isinstance(val[param_name], list):
                    raise ProcessingError(f"Dict parameter {param_name} is not of required type", str(val))
                if not all(isinstance(o, str) for o in val[param_name]):
                    raise ProcessingError(f"Elements of dict parameters {param_name} is not of required type", str(val))
                for x in val[param_name]:
                    _check_strlen(x, val, params["min_strlen"], params["max_strlen"])
                if len(val[param_name]) < params["min_len"]:
                    raise ProcessingError(f"Dict parameter {param_name} has too few elements", str(val))

        # Delete all parameters that are not in the template
        val: dict = {param_name: val[param_name] for param_name, _ in parameters}
    
    else:
        raise ValueError(f"Unknown output type: {required_type}")
