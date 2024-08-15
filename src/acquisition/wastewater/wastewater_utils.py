# general utilities (that should maybe migrate elsewhere)
def sig_digit_round(value, n_digits):
    """Truncate value to only n_digits.

    Truncate precision of elements in `value` (a numpy array) to the specified number of
    significant digits (9.87e5 would be 3 sig digits).
    """
    in_value = value
    value = np.asarray(value).copy()
    zero_mask = (value == 0) | np.isinf(value) | np.isnan(value)
    value[zero_mask] = 1.0
    sign_mask = value < 0
    value[sign_mask] *= -1
    exponent = np.ceil(np.log10(value))
    result = 10**exponent * np.round(value * 10 ** (-exponent), n_digits)
    result[sign_mask] *= -1
    result[zero_mask] = in_value[zero_mask]
    return result


def convert_df_type(df, type_dict, logger):
    """Convert types and warn if there are unexpected columns."""
    try:
        df = df.astype(type_dict)
    except KeyError as exc:
        raise KeyError(
            f"""
Expected column(s) missed, The dataset schema may
have changed. Please investigate and amend the code.

expected={''.join(sorted(type_dict.keys()))}
received={''.join(sorted(df.columns))}
"""
        ) from exc
    if new_columns := set(df.columns) - set(type_dict.keys()):
        logger.info("New columns found in NWSS dataset.", new_columns=new_columns)
    return df
