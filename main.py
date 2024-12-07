import argparse
import re
import sys
import yaml


def parse_args():
    parser = argparse.ArgumentParser(description="Инструмент преобразования YAML в учебный конфигурационный язык")
    parser.add_argument("input_file_path", type=str, help="Путь к YAML-файлу")
    return parser.parse_args()


def read_input_file(input_file_path):
    with open(input_file_path, "r", encoding="utf-8") as file:
        return file.read()


def validate_name(name):
    if not re.match(r'^[_a-zA-Z][_a-zA-Z0-9]*$', name):
        raise ValueError(f"Неверное имя: {name}")


def evaluate_expression(expression, constants):
    if expression.startswith('"') and expression.endswith('"'):
        expression = expression[1:-1]
    elif expression.startswith("'") and expression.endswith("'"):
        expression = expression[1:-1]
    if expression.startswith("!(") and expression.endswith(")"):
        expression = expression[2:-1]
    else:
        raise ValueError(f"Неправильный формат выражения: {expression}")
    for name, value in constants.items():
        expression = re.sub(rf'\b{name}\b', str(value), expression)
    allowed_globals = {
        "max": max,
        "print": print,
        **constants
    }
    try:
        result = eval(expression, {"__builtins__": None}, allowed_globals)
        return result
    except Exception as e:
        raise ValueError(f"Ошибка вычисления выражения '{expression}': {e}")


def format_value(value, constants):
    if isinstance(value, str) and value.startswith("!(") and value.endswith(")"):
        return str(evaluate_expression(value, constants))
    elif isinstance(value, (int, float, bool)):
        return value
    elif isinstance(value, str):
        return f'@"{value}"'
    elif isinstance(value, list):
        return " ".join([f'@"{v}"' if isinstance(v, str) else str(v) for v in value])
    elif isinstance(value, dict):
        return format_dict(value, constants)
    else:
        return "None"

def format_dict(data, constants):
    result = ["begin"]
    for key, value in data.items():
        result.append(f" {key} := {format_value(value, constants)};")
    result.append("end")
    return "\n".join(result)


def yaml_to_custom_format(yaml_content, constants):
    try:
        data = yaml.safe_load(yaml_content)
        if not isinstance(data, dict):
            raise ValueError("Корневой элемент должен быть словарём")
        data.pop("constants", None)
        return format_dict(data, constants)
    except yaml.YAMLError as e:
        raise ValueError(f"Ошибка разбора YAML: {e}")


def main():
    args = parse_args()
    try:
        yaml_content = read_input_file(args.input_file_path)
        parsed_data = yaml.safe_load(yaml_content)
        constants = parsed_data.get("constants", {})
        if not isinstance(constants, dict):
            raise ValueError("Секция 'constants' должна быть словарём")
        custom_format = yaml_to_custom_format(yaml_content, constants)
        print(custom_format)
    except Exception as e:
        print(f"Ошибка: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()