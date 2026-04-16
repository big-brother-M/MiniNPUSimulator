import time
from typing import List, Tuple

EPSILON = 1e-9


def normalize_label(label: str) -> str:
    """
    다양한 입력 라벨을 내부 표준 라벨로 정규화한다.
    내부 표준 라벨은 'Cross', 'X' 두 가지다.
    """
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


def mac(pattern: List[List[float]], filt: List[List[float]]) -> float:
    """
    pattern과 filt를 같은 위치끼리 곱한 뒤 모두 더한 MAC 점수를 반환한다.
    두 행렬은 같은 크기의 2차원 리스트여야 한다.
    """
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
    """
    Cross 점수와 X 점수를 비교해 최종 판정을 반환한다.
    점수 차이가 epsilon보다 작으면 UNDECIDED를 반환한다.
    """
    if abs(score_cross - score_x) < epsilon:
        return "UNDECIDED"
    elif score_cross > score_x:
        return "Cross"
    else:
        return "X"


def decide_ab(score_a: float, score_b: float, epsilon: float = EPSILON) -> str:
    """
    사용자 입력 모드용 판정 함수.
    score_a와 score_b를 비교해 A, B, 판정 불가를 반환한다.
    """
    if abs(score_a - score_b) < epsilon:
        return "판정 불가"
    elif score_a > score_b:
        return "A"
    else:
        return "B"


def parse_row_input(line: str, expected_size: int) -> List[float]:
    """
    한 줄 입력을 받아 expected_size개의 숫자로 이루어진 리스트로 변환한다.
    사용자 입력 모드에서는 0 또는 1만 허용한다.
    예:
        "0 1 0" -> [0.0, 1.0, 0.0]
    """
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


def input_matrix(size: int, title: str) -> List[List[float]]:
    """
    size x size 크기의 행렬을 사용자에게 입력받는다.
    각 줄의 입력이 잘못되면 안내 문구를 출력하고 같은 줄을 다시 입력받는다.
    """
    print(f"\n{title} ({size}줄 입력, 공백 구분)")
    matrix: List[List[float]] = []

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


def print_matrix(matrix: List[List[float]], title: str) -> None:
    """
    행렬을 보기 좋게 출력한다.
    """
    print(f"\n{title}")
    for row in matrix:
        row_text = []
        for value in row:
            if value.is_integer():
                row_text.append(str(int(value)))
            else:
                row_text.append(str(value))
        print(" ".join(row_text))


def measure_mac_time(pattern: List[List[float]], filt: List[List[float]], repeat: int = 10) -> Tuple[float, float]:
    """
    MAC 연산 1회의 평균 실행 시간(ms)을 측정한다.
    repeat 횟수만큼 반복 측정하고 평균값을 반환한다.
    반환값:
        (마지막 계산 점수, 평균 시간 ms)
    """
    total_ms = 0.0
    last_score = 0.0

    for _ in range(repeat):
        start = time.perf_counter()
        last_score = mac(pattern, filt)
        end = time.perf_counter()
        total_ms += (end - start) * 1000.0

    avg_ms = total_ms / repeat
    return last_score, avg_ms


def print_performance_analysis_3x3(avg_mac_ms: float, avg_classification_ms: float) -> None:
    """
    3x3 기준 성능 분석 결과를 표 형태로 출력한다.
    avg_mac_ms: MAC 1회 평균 시간
    avg_classification_ms: 필터 A/B 두 번 비교를 포함한 판정 1회 평균 시간(근사)
    """
    print("\n=== 성능 분석 (평균/10회) ===")
    print(f"{'크기':<10}{'평균 시간(ms)':<20}{'연산 횟수(N²)':<15}")
    print("-" * 45)
    print(f"{'3x3':<10}{avg_mac_ms:<20.6f}{9:<15}")

    print("\n참고:")
    print(f"- 위 표의 평균 시간은 '단일 MAC 1회' 기준입니다.")
    print(f"- 실제 판정 1회는 필터 A, B와 각각 비교하므로 MAC가 2번 수행됩니다.")
    print(f"- 따라서 현재 입력 기준 전체 판정 평균 시간은 약 {avg_classification_ms:.6f} ms 입니다.")


def run_step3_user_mode() -> None:
    """
    Step 3:
    사용자에게 3x3 필터 A, 필터 B, 패턴을 입력받고
    MAC 점수, 판정 결과, 연산 시간, 3x3 성능 분석을 출력한다.
    """
    print("=== Mini NPU Simulator - Step 3 ===")

    filter_a = input_matrix(3, "필터 A")
    filter_b = input_matrix(3, "필터 B")
    pattern = input_matrix(3, "패턴")

    print_matrix(filter_a, "입력된 필터 A")
    print_matrix(filter_b, "입력된 필터 B")
    print_matrix(pattern, "입력된 패턴")

    score_a = mac(pattern, filter_a)
    score_b = mac(pattern, filter_b)
    result = decide_ab(score_a, score_b)

    _, avg_a_ms = measure_mac_time(pattern, filter_a, repeat=10)
    _, avg_b_ms = measure_mac_time(pattern, filter_b, repeat=10)

    avg_mac_ms = (avg_a_ms + avg_b_ms) / 2.0
    avg_classification_ms = avg_a_ms + avg_b_ms

    print("\n=== MAC 결과 ===")
    print(f"A 점수: {score_a}")
    print(f"B 점수: {score_b}")
    print(f"연산 시간(평균/10회, 단일 MAC 기준): {avg_mac_ms:.6f} ms")
    print(f"판정: {result}")

    if result == "판정 불가":
        print(f"판정 불가 사유: |A-B| < {EPSILON}")

    print_performance_analysis_3x3(avg_mac_ms, avg_classification_ms)


if __name__ == "__main__":
    run_step3_user_mode()