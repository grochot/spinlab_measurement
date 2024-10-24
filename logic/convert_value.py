def convert_value(value):
    """
    Helper function to automatically convert string values to their proper types.
    """
    # Check for boolean
    if value.lower() == "true":
        return True
    elif value.lower() == "false":
        return False

    # Check for integer
    try:
        return int(value)
    except ValueError:
        pass

    # Check for float
    try:
        return float(value)
    except ValueError:
        pass

    # If none of the above, return the value as is (string)
    return value