import json


def generate_cross_pattern(n):
    matrix = [[0 for _ in range(n)] for _ in range(n)]
    mid = n // 2

    for i in range(n):
        matrix[i][mid] = 1
    for j in range(n):
        matrix[mid][j] = 1

    return matrix


def generate_x_pattern(n):
    matrix = [[0 for _ in range(n)] for _ in range(n)]

    for i in range(n):
        matrix[i][i] = 1
        matrix[i][n - 1 - i] = 1

    return matrix


def matrix_to_json_string(matrix, indent_level=0):
    indent = " " * indent_level
    row_indent = " " * (indent_level + 2)

    lines = ["["]
    for i, row in enumerate(matrix):
        row_str = ", ".join(str(value) for value in row)
        comma = "," if i < len(matrix) - 1 else ""
        lines.append(f"{row_indent}[{row_str}]{comma}")
    lines.append(f"{indent}]")
    return "\n".join(lines)


def build_data():
    data = {
        "filters": {},
        "patterns": {}
    }

    for size in [5, 13, 25]:
        cross = generate_cross_pattern(size)
        x_pattern = generate_x_pattern(size)

        data["filters"][f"size_{size}"] = {
            "cross": cross,
            "x": x_pattern
        }

        data["patterns"][f"size_{size}_1"] = {
            "input": cross,
            "expected": "+"
        }

        data["patterns"][f"size_{size}_2"] = {
            "input": x_pattern,
            "expected": "x"
        }

    return data


def save_pretty_data_json(data, path="data.json"):
    lines = ["{"]

    # filters
    lines.append('  "filters": {')
    filter_items = list(data["filters"].items())

    for i, (size_key, filter_group) in enumerate(filter_items):
        lines.append(f'    "{size_key}": {{')

        labels = list(filter_group.items())
        for j, (label, matrix) in enumerate(labels):
            lines.append(f'      "{label}": ' + matrix_to_json_string(matrix, indent_level=6) +
                         ("," if j < len(labels) - 1 else ""))

        lines.append("    }" + ("," if i < len(filter_items) - 1 else ""))

    lines.append("  },")

    # patterns
    lines.append('  "patterns": {')
    pattern_items = list(data["patterns"].items())

    for i, (case_id, case_data) in enumerate(pattern_items):
        lines.append(f'    "{case_id}": {{')
        lines.append('      "input": ' + matrix_to_json_string(case_data["input"], indent_level=6) + ",")
        lines.append(f'      "expected": "{case_data["expected"]}"')
        lines.append("    }" + ("," if i < len(pattern_items) - 1 else ""))

    lines.append("  }")
    lines.append("}")

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def main():
    data = build_data()
    save_pretty_data_json(data, "data.json")
    print("data.json 생성 완료")


if __name__ == "__main__":
    main()