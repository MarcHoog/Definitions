def to_snake_case(text: str) -> str:
    """
    Convert a string to snake_case.
    """
    for c in text:
        if c.isupper():
            text = text.replace(c, "_" + c.lower())

    return text.lower()


def append_to_file(
    file_path: str,
    content: str,
    mode: str = "a",
    encoding: str = "utf-8",
) -> None:
    """
    Append content to a file.
    """
    with open(file_path, mode, encoding=encoding) as file:
        file.write(content)


def create_new_file(
    file_path: str,
    content: str,
    mode: str = "w",
    encoding: str = "utf-8",
) -> None:
    """
    Create a new file with the given content.
    """
    with open(file_path, mode, encoding=encoding) as file:
        file.write(content)
