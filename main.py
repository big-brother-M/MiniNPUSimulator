EPSILON = 1e-9


def normalize_label(label: str) -> str:
    mapping = {
        "+": "Cross",
        "cross": "Cross",
        "Cross": "Cross",
        "x": "X",
        "X": "X",
    }

    if label not in mapping:
        raise ValueError(f"알 수 없는 라벨입니다: {label}")

    return mapping[label]


def mac(pattern: list[list[float]], filt: list[list[float]]) -> float:
    if len(pattern) != len(filt):
        raise ValueError("패턴과 필터의 행 크기가 다릅니다.")

    total = 0.0
    n = len(pattern)

    for i in range(n):
        if len(pattern[i]) != len(filt[i]):
            raise ValueError("패턴과 필터의 열 크기가 다릅니다.")

        for j in range(len(pattern[i])):
            total += pattern[i][j] * filt[i][j]

    return total


def decide_label(score_cross: float, score_x: float, epsilon: float = EPSILON) -> str:
    if abs(score_cross - score_x) < epsilon:
        return "UNDECIDED"
    elif score_cross > score_x:
        return "Cross"
    else:
        return "X"


def parse_row_input(line: str, expected_size: int) -> list[float]:
    parts = line.strip().split()

    if len(parts) != expected_size:
        raise ValueError(
            f"입력 형식 오류: 각 줄에 {expected_size}개의 숫자를 공백으로 구분해 입력하세요."
        )

    try:
        row = [float(value) for value in parts]
    except ValueError as e:
        raise ValueError(
            f"입력 형식 오류: 각 줄에 {expected_size}개의 숫자를 공백으로 구분해 입력하세요."
        ) from e

    for value in row:
        if value not in (0.0, 1.0):
            raise ValueError(
                "입력 값 오류: 사용자 입력 모드에서는 0 또는 1만 입력할 수 있습니다."
            )

    return row


def input_matrix(size: int, title: str) -> list[list[float]]:
    print(f"\n{title} ({size}줄 입력, 공백 구분)")
    matrix = []

    row_index = 0
    while row_index < size:
        line = input(f"{row_index + 1}번째 줄 입력: ").strip()

        try:
            row = parse_row_input(line, size)
            matrix.append(row)
            row_index += 1
        except ValueError as e:
            print(e)
            print("다시 입력해주세요.")

    return matrix


def print_matrix(matrix: list[list[float]], title: str) -> None:
    print(f"\n{title}")
    for row in matrix:
        print(" ".join(str(int(value)) if value.is_integer() else str(value) for value in row))


def run_step2_user_mode() -> None:
    print("=== Step 2: 사용자 입력(3x3) 데모 ===")

    filter_a = input_matrix(3, "필터 A")
    filter_b = input_matrix(3, "필터 B")
    pattern = input_matrix(3, "패턴")

    print_matrix(filter_a, "입력된 필터 A")
    print_matrix(filter_b, "입력된 필터 B")
    print_matrix(pattern, "입력된 패턴")

    score_a = mac(pattern, filter_a)
    score_b = mac(pattern, filter_b)

    if abs(score_a - score_b) < EPSILON:
        result = "판정 불가"
    elif score_a > score_b:
        result = "A"
    else:
        result = "B"

    print("\n=== MAC 결과 ===")
    print(f"A 점수: {score_a}")
    print(f"B 점수: {score_b}")
    print(f"판정: {result}")


if __name__ == "__main__":
    run_step2_user_mode()