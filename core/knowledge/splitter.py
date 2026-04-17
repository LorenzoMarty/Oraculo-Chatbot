def split_text(text, size=1000):
    return [text[i : i + size] for i in range(0, len(text), size)]
