import json

# & % $ # _ { } ~ ^ \
special_characters_mapping = {
    # "&": "&#38;",  # Ampersand
    # "%": "&#37;",  # Percent sign
    # "$": "&#36;",  # Dollar sign 
    # "#": "&#35;",  # Number sign 
    # "_": "&#95;",  # Underscore
    "{": "&#123;", # Opening/Left curly brace
    "}": "&#125;", # Closing/Right curly brace
    # "~": "&#126;", # Tilde
    # "^": "&#94;",  # Caret
    # "\\": "&#92;", # Backslash
}

def __dict_replace(s, d):
    """Replace substrings of a string using a dictionary."""
    for key, value in d.items():
        s = s.replace(key, value)
    return s

def escape_special_characters(input: str) -> str:
    return __dict_replace(input, 
                          special_characters_mapping)
    


def toml_string(value) -> str:
    """Encode a value as a TOML basic (double quoted, single line) string.

    JSON string escapes are valid TOML escapes. Non-ASCII characters are kept
    as they are (a JSON ``\\ud83d\\ude00`` surrogate pair is not valid TOML) and
    DEL, which TOML forbids unescaped, is escaped explicitly.
    """
    encoded = json.dumps("" if value is None else str(value), ensure_ascii=False)
    return encoded.replace("\x7f", "\\u007f")
