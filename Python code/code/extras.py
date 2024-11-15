def fraction_to_float(fraction_str):
    if '/' in fraction_str:
        numerator, denominator = fraction_str.split('/')
        try:
            return float(numerator) / float(denominator)
        except ZeroDivisionError:
            print("Error: Denominator cannot be zero.")
    else:
        try:
            return float(fraction_str)
        except ValueError:
            print(f"Error converting '{fraction_str}' to float.")


def convert_to_forward_slashes(path):
    # Replace backslashes with forward slashes
    return path.replace('\\', '/')