import json
import pkgutil
import random
import string
from collections import namedtuple
from datetime import datetime, timedelta
from math import ceil, inf, log2
from typing import Iterable

import numpy as np


def dedupe_preserving_order(list_of_items):
    return list(dict.fromkeys(list_of_items))


def prob_to_bayes_factor(prob):
    return prob / (1 - prob) if prob != 1 else inf


def prob_to_match_weight(prob):
    return log2(prob_to_bayes_factor(prob))


def match_weight_to_bayes_factor(weight):
    return 2**weight


def bayes_factor_to_prob(bf):
    return bf / (1 + bf)


def interpolate(start, end, num_elements):
    steps = num_elements - 1
    step = (end - start) / steps
    vals = [start + (i * step) for i in range(0, num_elements)]
    return vals


def normalise(vals):
    return [v / sum(vals) for v in vals]


def ensure_is_iterable(a):
    return a if isinstance(a, Iterable) else [a]


def ensure_is_list(a):
    return a if isinstance(a, list) else [a]


def ensure_is_tuple(a):
    if isinstance(a, tuple):
        return a
    elif isinstance(a, list):
        return tuple(a)
    else:
        return (a,)


def join_list_with_commas_final_and(lst):
    if len(lst) == 1:
        return lst[0]
    return ", ".join(lst[:-1]) + " and " + lst[-1]


class EverythingEncoder(json.JSONEncoder):
    """
    Used to correctly encode data when dumping it to json where we need to
    hardcode json into javascript in a .html file for e.g. comparison viewer

    Without this, json.dumps errors if given an a column of class int32, int64
    np.array, datetime.date etc.

    Thanks to:
    https://github.com/mpld3/mpld3/issues/434#issuecomment-340255689
    """

    # Note that the default method is only called for data types that are
    # NOT natively serializable.  The 'encode' method can be used
    # for natively serializable data
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.bool_):
            return bool(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        try:
            return json.JSONEncoder.default(self, obj)
        except TypeError:
            return obj.__str__()


def calculate_cartesian(df_rows, link_type):
    """
    Calculates the cartesian product for the input df(s).
    """
    n = df_rows

    if link_type == "link_only":
        if len(n) <= 1:
            raise ValueError(
                "if 'link_type 'is 'link_only' should have " "at least two input frames"
            )
        # sum of pairwise product can be found as
        # half of [(sum)-squared - (sum of squares)]
        return (
            sum([m["count"] for m in n]) ** 2 - sum([m["count"] ** 2 for m in n])
        ) / 2

    if link_type == "dedupe_only":
        if len(n) > 1:
            raise ValueError(
                "if 'link_type' is 'dedupe_only' should have only "
                "a single input frame"
            )
        return n[0]["count"] * (n[0]["count"] - 1) / 2

    if link_type == "link_and_dedupe":
        total_rows = sum([m["count"] for m in n])
        return total_rows * (total_rows - 1) / 2

    raise ValueError(
        "'link_type' should be either 'link_only', 'dedupe_only', "
        "or 'link_and_dedupe'"
    )


def calculate_reduction_ratio(N, cartesian):
    """
    Args:
        N (int): The number of record pairs generated by a
            blocking rule.
        cartesian (int): The cartesian product of your input
            dataframe(s).

    Generates the reduction ratio. This represents the % reduction
    in the comparison space as a result of using your given blocking
    rule. This is a measure of how much the Blocking Rule reduces
    the total search space.
    """
    return 1 - (N / cartesian)


def major_minor_version_greater_equal_than(this_version, base_comparison_version):
    this_version = this_version.split(".")[:2]
    this_version = [v.zfill(10) for v in this_version]

    base_version = base_comparison_version.split(".")[:2]
    base_version = [v.zfill(10) for v in base_version]

    return this_version >= base_version


def ascii_uid(len):
    # use only lowercase as case-sensitivity is an issue in e.g. postgres
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=len))


def find_unique_source_dataset(src_ds):
    sql = f"""
        select distinct {src_ds} as src
        from __splink__df_concat_with_tf
    """

    return sql


def parse_duration(duration: int):
    # math.ceil so <1 second gets reported
    d = datetime(1, 1, 1) + timedelta(seconds=int(ceil(duration)))
    time_index = namedtuple("Time", ["Days", "Hours", "Minutes", "Seconds"])
    duration = time_index(d.day - 1, d.hour, d.minute, d.second)
    txt_duration = [
        f"{t} {duration._fields[n]}" for n, t in enumerate(duration) if t > 0
    ]
    if len(txt_duration) > 1:
        txt_duration[-1] = "and " + txt_duration[-1]

    return ", ".join(txt_duration)


class colour:
    """A class to beautify your text. Simply import and then use this class's
    attributes to adjust how the text is formatted. For example:

    `f"{colour.BOLD}Send help{colour.END}`

    will print your text to the console in bold.
    """

    PURPLE = "\033[95m"
    CYAN = "\033[96m"
    DARKCYAN = "\033[36m"
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    ITALICS = "\033[3m"
    END = "\033[0m"


def read_resource(path: str) -> str:
    """Reads a resource file from the splink package"""
    # In the future we may have to move to importlib.resources
    # https://github.com/python/cpython/issues/89838#issuecomment-1093935933
    # But for now this API avoids having to do conditional imports
    # depending on python version.
    # Also, if you use importlib.resources, then you have to add an
    # __init__.py file to every subdirectory, which is annoying.
    return pkgutil.get_data("splink", path).decode("utf-8")
