from typing import List


def validate_pattern_size(n: int) -> None:
    """
    패턴 생성기에 사용할 크기 N이 유효한지 검사한다.
    """
    if n <= 0:
        raise ValueError("크기 N은 1 이상의 정수여야 합니다.")


def generate_cross_pattern(n: int) -> List[List[float]]:
    """
    n x n Cross 패턴을 생성한다.
    가운데 행 전체와 가운데 열 전체를 1로 둔다.
    """
    validate_pattern_size(n)

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
    validate_pattern_size(n)

    matrix = [[0.0 for _ in range(n)] for _ in range(n)]

    for i in range(n):
        matrix[i][i] = 1.0
        matrix[i][n - 1 - i] = 1.0

    return matrix


def generate_pattern_from_label(label: str, size: int) -> List[List[float]]:
    """
    표준 라벨(Cross/X)과 크기 N을 받아 해당 패턴을 생성한다.
    """
    if label == "Cross":
        return generate_cross_pattern(size)
    if label == "X":
        return generate_x_pattern(size)

    raise ValueError(f"지원하지 않는 패턴 라벨입니다: {label}")
