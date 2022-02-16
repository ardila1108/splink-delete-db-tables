def null_level(col_name):
    return {
        "sql_condition": f"{col_name}_l IS NULL OR {col_name}_r IS NULL",
        "label_for_charts": "Null",
        "is_null_level": True,
    }


def exact_match_level(col_name, m_probability=None, term_frequency_adjustments=False):
    d = {
        "sql_condition": f"{col_name}_l = {col_name}_r",
        "label_for_charts": "exact_match",
        "m_probability": m_probability,
    }
    if term_frequency_adjustments:
        d["tf_adjustment_column"] = col_name
    if m_probability:
        d["m_probability"] = m_probability
    return d


def levenshtein_level(col_name, distance_threshold, m_probability=None):
    d = {
        "sql_condition": f"levenshtein({col_name}_l, {col_name}_r) <= {distance_threshold}",
        "label_for_charts": f"Levenstein <= {distance_threshold}",
    }
    if m_probability:
        d["m_probability"] = m_probability

    return d


def else_level(
    col_name=None,
    m_probability=None,
):
    d = {
        "sql_condition": "ELSE",
        "label_for_charts": "All other comparisons",
    }
    if m_probability:
        d["m_probability"] = m_probability
    return d
