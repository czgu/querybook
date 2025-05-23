from typing import Any, Dict, List, Literal, TypedDict, Union
from lib.config import get_config_value

cell_types = get_config_value("datadoc.cell_types")


def get_valid_meta(input_vals, valid_vals, default_vals=None):
    if input_vals is None:
        return default_vals

    if not check_type_match(input_vals, valid_vals):
        raise ValueError(
            f"Invalid meta type, expected {type(valid_vals)} actual {type(input_vals)}"
        )

    if isinstance(valid_vals, dict):
        return_obj = {}
        for valid_key, valid_val in valid_vals.items():
            if valid_key in input_vals:
                # only for series object for chart y_axis
                if valid_key == "series" and type(valid_val) is dict and 0 in valid_val:
                    if _validate_series(valid_val, input_vals["series"]):
                        return_obj[valid_key] = input_vals["series"]
                    else:
                        raise ValueError("Invalid meta type for axis series")
                else:
                    # Normal case, iterate all keys
                    return_obj[valid_key] = get_valid_meta(
                        input_vals=input_vals[valid_key],
                        valid_vals=valid_val,
                        default_vals=(
                            default_vals.get(valid_key) if default_vals else None
                        ),
                    )
        return return_obj
    elif isinstance(valid_vals, list):
        return [
            get_valid_meta(
                input_vals=input_val,
                valid_vals=valid_vals[0],
                default_vals=(default_vals or [None])[0],
            )
            for input_val in input_vals
        ]
    else:
        return input_vals


def _validate_series(valid_val, input_val):
    valid_series_keys = valid_val[0].keys()
    # Do a shallow key validation
    return all(
        all([item_key in valid_series_keys for item_key in series_item])
        for series_item in input_val.values()
    )


def sanitize_data_cell_meta(cell_type: str, meta):
    cell_type_info = cell_types[cell_type]

    valid_dict = cell_type_info["meta"]
    default_dict = cell_type_info["meta_default"]

    if meta is None:
        return default_dict

    return get_valid_meta(
        input_vals=meta, valid_vals=valid_dict, default_vals=default_dict
    )


def check_type_match(actual_val, expected_val) -> bool:
    """Check actual_val matches type of expected_val
       The exception here is that expected_val can be
       float, and in that case actual_val can be either
       int or float

    Args:
        actual_val (Any): Actual type
        expected_val (Any): Expected type

    Returns:
        bool: Whether the type matches
    """
    if type(actual_val) == type(expected_val):
        return True

    # Make an exception here since int can be represented as float
    # But not vice versa (for example, index)
    if type(expected_val) == float and type(actual_val) == int:
        return True

    return False


class PythonDataFrameOutput(TypedDict):
    type: Literal["dataframe"]
    data: Dict[str, Union[List[str], List[Dict[str, Any]]]]


class PythonImageOutput(TypedDict):
    type: Literal["image"]
    data: str


class PythonJsonOutput(TypedDict):
    type: Literal["json"]
    data: Dict[str, Any]


PythonOutputType = Union[
    PythonDataFrameOutput, PythonImageOutput, PythonJsonOutput, str
]


def validate_python_output(output: PythonOutputType) -> None:
    if not isinstance(output, list):
        raise ValueError("Output must be a list.")

    for item in output:
        if not isinstance(item, (str, dict)):
            raise ValueError(
                "Each element in the output must be either a string or a dictionary."
            )
        if isinstance(item, dict):
            if "type" not in item or "data" not in item:
                raise ValueError(
                    "Each dictionary in the output must contain 'type' and 'data' keys."
                )
            if item["type"] not in {"dataframe", "image", "json"}:
                raise ValueError(
                    "The 'type' key in the dictionary must be one of 'dataframe', 'image', or 'json'."
                )
            if item["type"] == "dataframe":
                if "columns" not in item["data"] or "records" not in item["data"]:
                    raise ValueError(
                        "The 'data' dictionary must contain 'columns' and 'records' keys."
                    )
                if not isinstance(item["data"]["columns"], list):
                    raise ValueError(
                        "The 'columns' key in the 'data' dictionary must be a list."
                    )
                if not isinstance(item["data"]["records"], list):
                    raise ValueError(
                        "The 'records' key in the 'data' dictionary must be a list."
                    )
