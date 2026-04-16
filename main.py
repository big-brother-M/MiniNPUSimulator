import json
import time
from typing import Any, Dict, List, Optional, Tuple

EPSILON = 1e-9


def print_section(title: str) -> None:
    print("\n" + "=" * 50)
    print(title)
    print("=" * 50)


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
    if score_cross > score_x:
        return "Cross"
    return "X"


def decide_ab(score_a: float, score_b: float, epsilon: float = EPSILON) -> str:
    """
    사용자 입력 모드용 판정 함수.
    score_a와 score_b를 비교해 A, B, 판정 불가를 반환한다.
    """
    if abs(score_a - score_b) < epsilon:
        return "판정 불가"
    if score_a > score_b:
        return "A"
    return "B"


def parse_row_input(line: str, expected_size: int) -> List[float]:
    """
    한 줄 입력을 받아 expected_size개의 숫자로 이루어진 리스트로 변환한다.
    사용자 입력 모드에서는 0 또는 1만 허용한다.
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


def measure_mac_time(
    pattern: List[List[float]],
    filt: List[List[float]],
    repeat: int = 10,
) -> Tuple[float, float]:
    """
    MAC 연산 1회의 평균 실행 시간(ms)을 측정한다.
    repeat 횟수만큼 반복 측정하고 평균값을 반환한다.
    반환값: (마지막 계산 점수, 평균 시간 ms)
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
    print("- 위 표의 평균 시간은 '단일 MAC 1회' 기준입니다.")
    print("- 실제 판정 1회는 필터 A, B와 각각 비교하므로 MAC가 2번 수행됩니다.")
    print(f"- 현재 입력 기준 전체 판정 평균 시간은 약 {avg_classification_ms:.6f} ms 입니다.")


def run_user_mode() -> None:
    """
    사용자 입력(3x3) 모드
    """
    print_section("Mini NPU Simulator - 사용자 입력 모드 (3x3)")

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

    print_section("MAC 결과")
    print(f"A 점수: {score_a}")
    print(f"B 점수: {score_b}")
    print(f"연산 시간(평균/10회, 단일 MAC 기준): {avg_mac_ms:.6f} ms")
    print(f"판정: {result}")

    if result == "판정 불가":
        print(f"판정 불가 사유: |A-B| < {EPSILON}")

    print_performance_analysis_3x3(avg_mac_ms, avg_classification_ms)


def load_json_file(path: str = "data.json") -> Dict[str, Any]:
    """
    data.json 파일을 로드한다.
    """
    try:
        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError as e:
        raise FileNotFoundError(
            f"파일을 찾을 수 없습니다: {path}\n"
            "main.py와 같은 폴더에 data.json이 있는지 확인하세요."
        ) from e
    except json.JSONDecodeError as e:
        raise ValueError(
            f"JSON 파싱 오류: {e}\n"
            "data.json 문법이 올바른지 확인하세요."
        ) from e

    if not isinstance(data, dict):
        raise ValueError("JSON 최상위 구조는 객체(dict)여야 합니다.")

    return data


def validate_json_structure(data: Dict[str, Any]) -> None:
    """
    JSON 최상위 구조가 요구사항에 맞는지 확인한다.
    필수 키: filters, patterns
    """
    if "filters" not in data:
        raise ValueError("JSON 구조 오류: 최상위에 'filters' 키가 없습니다.")
    if "patterns" not in data:
        raise ValueError("JSON 구조 오류: 최상위에 'patterns' 키가 없습니다.")

    if not isinstance(data["filters"], dict):
        raise ValueError("JSON 구조 오류: 'filters'는 객체(dict)여야 합니다.")
    if not isinstance(data["patterns"], dict):
        raise ValueError("JSON 구조 오류: 'patterns'는 객체(dict)여야 합니다.")


def extract_size_from_pattern_key(key: str) -> int:
    """
    패턴 키에서 size를 추출한다.
    예:
        size_5_1 -> 5
        size_13_2 -> 13
    """
    parts = key.split("_")

    if len(parts) < 3:
        raise ValueError(f"패턴 키 형식 오류: {key}")

    if parts[0] != "size":
        raise ValueError(f"패턴 키 형식 오류: {key}")

    try:
        size = int(parts[1])
    except ValueError as e:
        raise ValueError(f"패턴 키에서 크기를 추출할 수 없습니다: {key}") from e

    return size


def validate_square_matrix(matrix: Any, expected_size: Optional[int] = None) -> Tuple[bool, str]:
    """
    2차원 정사각 행렬인지 검증한다.
    JSON 모드에서는 int/float 숫자만 허용한다.
    """
    if not isinstance(matrix, list):
        return False, "행렬이 list가 아닙니다."

    if len(matrix) == 0:
        return False, "행렬이 비어 있습니다."

    row_count = len(matrix)

    if expected_size is not None and row_count != expected_size:
        return False, f"행 수가 기대 크기와 다릅니다. expected={expected_size}, actual={row_count}"

    for row_index, row in enumerate(matrix):
        if not isinstance(row, list):
            return False, f"{row_index}번째 행이 list가 아닙니다."

        if len(row) != row_count:
            return False, f"{row_index}번째 행 길이가 정사각형 조건과 맞지 않습니다."

        if expected_size is not None and len(row) != expected_size:
            return False, f"{row_index}번째 행의 열 수가 기대 크기와 다릅니다."

        for col_index, value in enumerate(row):
            if not isinstance(value, (int, float)):
                return False, (
                    f"숫자가 아닌 값이 포함되어 있습니다. "
                    f"(row={row_index}, col={col_index}, value={value})"
                )

    return True, ""


def convert_matrix_to_float(matrix: List[List[Any]]) -> List[List[float]]:
    """
    int/float가 섞인 2차원 리스트를 float 2차원 리스트로 변환한다.
    """
    return [[float(value) for value in row] for row in matrix]

def generate_cross_pattern(n: int) -> List[List[float]]:
    """
    n x n Cross 패턴을 생성한다.
    가운데 행 전체와 가운데 열 전체를 1로 둔다.
    """
    matrix = [[0.0 for _ in range(n)] for _ in range(n)]
    mid = n // 2

    for i in range(n):
        matrix[i][mid] = 1.0

    for j in range(n):
        matrix[mid][j] = 1.0

    return matrix


def generate_x_pattern(n: int) -> List[List[float]]:
    """
    n x n X 패턴을 생성한다.
    주대각선과 부대각선을 1로 둔다.
    """
    matrix = [[0.0 for _ in range(n)] for _ in range(n)]

    for i in range(n):
        matrix[i][i] = 1.0
        matrix[i][n - 1 - i] = 1.0

    return matrix


def benchmark_single_size(
    pattern: List[List[float]],
    filt: List[List[float]],
    repeat: int = 10,
) -> float:
    """
    주어진 pattern과 filt에 대해 MAC 1회의 평균 시간(ms)을 반환한다.
    """
    _, avg_ms = measure_mac_time(pattern, filt, repeat=repeat)
    return avg_ms


def print_performance_table(rows: List[Dict[str, Any]]) -> None:
    """
    성능 분석 결과 표를 출력한다.
    rows 예시:
    [
        {"size": 3, "avg_ms": 0.01, "ops": 9, "source": "generated"},
        ...
    ]
    """
    print_section("성능 분석 (평균/10회)")
    print(f"{'크기(NxN)':<15}{'평균 시간(ms)':<20}{'연산 횟수(N²)':<18}{'데이터 출처'}")
    print("-" * 70)

    for row in rows:
        size_text = f"{row['size']}x{row['size']}"
        avg_ms_text = f"{row['avg_ms']:.6f}"
        ops_text = str(row["ops"])
        source_text = row["source"]

        print(f"{size_text:<15}{avg_ms_text:<20}{ops_text:<18}{source_text}")


def run_performance_analysis(
    filters_by_size: Dict[int, Dict[str, List[List[float]]]],
    repeat: int = 10,
) -> None:
    """
    3x3, 5x5, 13x13, 25x25 성능 분석을 수행한다.
    - 3x3은 생성기로 만든 Cross 패턴/필터 사용
    - 5/13/25는 JSON에서 로드한 Cross 필터 사용
    """
    rows: List[Dict[str, Any]] = []

    # 3x3은 JSON에 없을 수 있으므로 생성기로 직접 준비
    cross_3 = generate_cross_pattern(3)
    avg_3 = benchmark_single_size(cross_3, cross_3, repeat=repeat)
    rows.append({
        "size": 3,
        "avg_ms": avg_3,
        "ops": 3 * 3,
        "source": "generated (Cross vs Cross)"
    })

    # JSON 필터에서 5, 13, 25를 가져와 측정
    for size in [5, 13, 25]:
        if size not in filters_by_size:
            rows.append({
                "size": size,
                "avg_ms": -1.0,
                "ops": size * size,
                "source": "missing filter"
            })
            continue

        cross_filter = filters_by_size[size]["Cross"]
        cross_pattern = generate_cross_pattern(size)

        avg_ms = benchmark_single_size(cross_pattern, cross_filter, repeat=repeat)
        rows.append({
            "size": size,
            "avg_ms": avg_ms,
            "ops": size * size,
            "source": "data.json filter (Cross)"
        })

    print_performance_table_with_missing_support(rows)

def print_performance_table_with_missing_support(rows: List[Dict[str, Any]]) -> None:
    """
    missing filter 상황까지 포함해서 성능 표를 출력한다.
    """
    print_section("성능 분석 (평균/10회)")
    print(f"{'크기(NxN)':<15}{'평균 시간(ms)':<20}{'연산 횟수(N²)':<18}{'데이터 출처'}")
    print("-" * 70)

    for row in rows:
        size_text = f"{row['size']}x{row['size']}"
        ops_text = str(row["ops"])
        source_text = row["source"]

        if row["avg_ms"] < 0:
            avg_ms_text = "N/A"
        else:
            avg_ms_text = f"{row['avg_ms']:.6f}"

        print(f"{size_text:<15}{avg_ms_text:<20}{ops_text:<18}{source_text}")

    print("\n참고:")
    print("- 위 시간은 I/O를 제외한 'MAC 함수 호출 구간'만 반복 측정한 평균값입니다.")
    print("- MAC 1회는 n x n 원소를 모두 방문하므로 연산 횟수는 N²입니다.")
    print("- 실제 분류는 Cross 필터와 X 필터 각각에 대해 MAC를 수행하므로, 판정 1회에는 MAC가 2번 사용됩니다.")

def build_normalized_filters(
    raw_filters: Dict[str, Any]
) -> Tuple[Dict[int, Dict[str, List[List[float]]]], List[str]]:
    """
    filters 섹션을 내부 표준 구조로 변환한다.

    반환 예시:
    {
        5: {"Cross": [...], "X": [...]},
        13: {"Cross": [...], "X": [...]}
    }

    warnings에는 로드되지 못한 필터 관련 경고 메시지를 모은다.
    """
    normalized_filters: Dict[int, Dict[str, List[List[float]]]] = {}
    warnings: List[str] = []

    for size_key, filter_group in raw_filters.items():
        if not isinstance(size_key, str) or not size_key.startswith("size_"):
            warnings.append(f"{size_key}: size_N 형식의 키가 아닙니다.")
            continue

        parts = size_key.split("_")
        if len(parts) != 2:
            warnings.append(f"{size_key}: size_N 형식이 아닙니다.")
            continue

        try:
            size = int(parts[1])
        except ValueError:
            warnings.append(f"{size_key}: 크기를 정수로 해석할 수 없습니다.")
            continue

        if not isinstance(filter_group, dict):
            warnings.append(f"{size_key}: 필터 그룹이 dict가 아닙니다.")
            continue

        current_group: Dict[str, List[List[float]]] = {}

        for raw_label, matrix in filter_group.items():
            try:
                normalized_label = normalize_label(raw_label)
            except ValueError:
                warnings.append(f"{size_key}: 알 수 없는 필터 라벨 '{raw_label}'")
                continue

            valid, message = validate_square_matrix(matrix, expected_size=size)
            if not valid:
                warnings.append(f"{size_key}/{normalized_label}: {message}")
                continue

            current_group[normalized_label] = convert_matrix_to_float(matrix)

        if "Cross" not in current_group or "X" not in current_group:
            warnings.append(f"{size_key}: Cross/X 필터가 모두 준비되지 않았습니다.")
            continue

        normalized_filters[size] = {
            "Cross": current_group["Cross"],
            "X": current_group["X"],
        }

    return normalized_filters, warnings


def analyze_pattern_case(
    case_id: str,
    case_data: Any,
    filters_by_size: Dict[int, Dict[str, List[List[float]]]],
    epsilon: float = EPSILON,
) -> Dict[str, Any]:
    """
    pattern 케이스 하나를 분석한다.
    케이스 하나가 실패해도 프로그램 전체가 중단되지 않도록
    결과 dict로 PASS/FAIL 및 원인을 반환한다.
    """
    result: Dict[str, Any] = {
        "case_id": case_id,
        "score_cross": None,
        "score_x": None,
        "predicted": None,
        "expected": None,
        "status": "FAIL",
        "reason": "",
    }

    try:
        size = extract_size_from_pattern_key(case_id)

        if not isinstance(case_data, dict):
            result["reason"] = "케이스 데이터가 dict가 아닙니다."
            return result

        if "input" not in case_data:
            result["reason"] = "input 필드가 없습니다."
            return result

        if "expected" not in case_data:
            result["reason"] = "expected 필드가 없습니다."
            return result

        if size not in filters_by_size:
            result["reason"] = f"size_{size}에 해당하는 유효한 필터가 없습니다."
            return result

        expected_raw = case_data["expected"]
        expected = normalize_label(str(expected_raw))
        result["expected"] = expected

        pattern_raw = case_data["input"]
        valid, message = validate_square_matrix(pattern_raw, expected_size=size)
        if not valid:
            result["reason"] = f"패턴 검증 실패: {message}"
            return result

        pattern = convert_matrix_to_float(pattern_raw)
        cross_filter = filters_by_size[size]["Cross"]
        x_filter = filters_by_size[size]["X"]

        score_cross = mac(pattern, cross_filter)
        score_x = mac(pattern, x_filter)
        predicted = decide_label(score_cross, score_x, epsilon)

        result["score_cross"] = score_cross
        result["score_x"] = score_x
        result["predicted"] = predicted

        if predicted == expected:
            result["status"] = "PASS"
            result["reason"] = ""
        else:
            result["status"] = "FAIL"
            if predicted == "UNDECIDED":
                result["reason"] = "동점 규칙에 따라 UNDECIDED로 판정되었습니다."
            else:
                result["reason"] = f"expected={expected}, predicted={predicted}"

        return result

    except Exception as e:
        result["reason"] = f"예외 발생: {e}"
        return result


def pattern_sort_key(case_id: str) -> Tuple[int, str]:
    """
    패턴 케이스를 size 기준으로 정렬하기 위한 키
    """
    try:
        return extract_size_from_pattern_key(case_id), case_id
    except Exception:
        return 10**9, case_id


def print_case_result(result: Dict[str, Any]) -> None:
    """
    케이스 하나의 분석 결과를 출력한다.
    """
    print(f"\n--- {result['case_id']} ---")

    if result["score_cross"] is not None:
        print(f"Cross 점수: {result['score_cross']}")
    if result["score_x"] is not None:
        print(f"X 점수: {result['score_x']}")
    if result["predicted"] is not None:
        print(f"판정: {result['predicted']}")
    if result["expected"] is not None:
        print(f"expected: {result['expected']}")

    if result["status"] == "PASS":
        print("결과: PASS")
    else:
        print(f"결과: FAIL")
        print(f"사유: {result['reason']}")


def print_summary(results: List[Dict[str, Any]]) -> None:
    """
    전체 테스트 결과 요약 출력
    """
    total = len(results)
    passed = sum(1 for item in results if item["status"] == "PASS")
    failed = total - passed

    print_section("결과 요약")
    print(f"총 테스트: {total}개")
    print(f"통과: {passed}개")
    print(f"실패: {failed}개")

    if failed > 0:
        print("\n실패 케이스:")
        for item in results:
            if item["status"] == "FAIL":
                print(f"- {item['case_id']}: {item['reason']}")


def run_json_mode() -> None:
    """
    data.json 분석 모드
    - 필터 로드 및 정규화
    - 패턴별 MAC 연산
    - PASS/FAIL 판정
    - 결과 요약 출력
    """
    print_section("Mini NPU Simulator - data.json 분석 모드")

    try:
        data = load_json_file("data.json")
        validate_json_structure(data)
    except Exception as e:
        print(f"JSON 로드 실패: {e}")
        return

    filters_by_size, filter_warnings = build_normalized_filters(data["filters"])

    print_section("필터 로드 결과")
    if filters_by_size:
        for size in sorted(filters_by_size.keys()):
            print(f"✓ size_{size} 필터 로드 완료 (Cross, X)")
    else:
        print("유효한 필터가 하나도 없습니다.")

    if filter_warnings:
        print("\n필터 경고:")
        for warning in filter_warnings:
            print(f"- {warning}")

    print_section("패턴 분석")
    results: List[Dict[str, Any]] = []

    for case_id in sorted(data["patterns"].keys(), key=pattern_sort_key):
        case_data = data["patterns"][case_id]
        result = analyze_pattern_case(case_id, case_data, filters_by_size, epsilon=EPSILON)
        results.append(result)
        print_case_result(result)

    print_summary(results)
    run_performance_analysis(filters_by_size, repeat=10)


def select_mode() -> str:
    """
    사용자에게 실행 모드를 입력받는다.
    1: 사용자 입력(3x3)
    2: data.json 분석
    """
    while True:
        print_section("Mini NPU Simulator")
        print("[모드 선택]")
        print("1. 사용자 입력 (3x3)")
        print("2. data.json 분석")
        choice = input("선택: ").strip()

        if choice in ("1", "2"):
            return choice

        print("입력 오류: 1 또는 2만 입력할 수 있습니다.")


def main() -> None:
    choice = select_mode()

    if choice == "1":
        run_user_mode()
    else:
        run_json_mode()


if __name__ == "__main__":
    main()