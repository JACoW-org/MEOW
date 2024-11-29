

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
    
