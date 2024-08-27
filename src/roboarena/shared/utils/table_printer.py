import time
from dataclasses import dataclass
from functools import partial
from typing import Any


@dataclass(frozen=True)
class Seperator:
    vertical: str = "|"
    horizontal: str = "-"
    intersection: str = "+"
    # seperator: str = "-"


def calculate_width(data: list[list[Any]]) -> list[int]:
    row_item_widths: list[list[int]] = [[] for _ in range(len(data[0]))]
    for row in data:
        for i, element in enumerate(row):
            row_item_widths[i].append(len(f"{element}"))
    return [max(col) for col in row_item_widths]


def fetch_entry(row: int, col: int, data: list[list[Any]]) -> Any:
    if len(data) <= row or row < 0:
        return ""
    if len(data[row]) <= col or col < 0:
        return ""
    return data[row][col]


def seperator(col_widths: list[int], sep: Seperator):
    elements: list[str] = []
    for width in col_widths:
        elements.append(sep.horizontal * (width + 2))
    return sep.intersection + sep.intersection.join(elements) + sep.intersection


def construct_row(row: list[Any], col_widths: list[int], sep: Seperator) -> str:
    elements: list[str] = []
    for i, element in enumerate(row):
        padding = " " * (col_widths[i] - len(f"{element}"))
        elements.append(f" {element}{padding} ")
    return f"{sep.vertical}{sep.vertical.join(elements)}{sep.vertical}"


def max_bounds(data: list[list[Any]]) -> tuple[int, int]:
    return len(data), max([len(row) for row in data])


def construct_table(
    data: list[list[Any]], sep: Seperator, seperate_lines: bool = False
) -> list[str]:
    max_r, max_c = max_bounds(data)
    updated_data = [
        [fetch_entry(j, i, data) for i in range(max_c)] for j in range(max_r)
    ]
    col_width = calculate_width(updated_data)
    constructed_seperator = seperator(col_width, sep)
    const_row_part = partial(construct_row, col_widths=col_width, sep=sep)
    output: list[str] = [constructed_seperator]
    for row_i, row in enumerate(updated_data):
        if "__sep" in row:
            output.append(constructed_seperator)
            continue
        output.append(const_row_part(row))
        if seperate_lines and row_i != len(data) - 1:
            output.append(constructed_seperator)
    output.append(constructed_seperator)
    return output


def print_table(
    data: list[list[Any]], sep: Seperator = Seperator()  # noqa: B008
) -> None:
    lines = construct_table(data, sep, False)
    print("\n".join(lines), flush=True)


if __name__ == "__main__":

    config = [
        ["Coin", "Amount", "Euro Value"],
        ["__sep"],
        ["BTC", 0.18576332, 4136],
        ["ETH", 270.35 / 1537.9, 270.35],
        ["__sep"],
        ["XMR", 172.367 / 141.9, 172.367],
    ]
    for _ in range(10):
        print_table(config)
        time.sleep(1)
