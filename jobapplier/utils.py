def read_file_as_string(path: str) -> str:
    """Read the entire contents of a file and return it as a string."""
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()
