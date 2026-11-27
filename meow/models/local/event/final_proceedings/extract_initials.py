import re

def extract_initials(name: str, keep_compound_hyphen: bool = True, separator: str = ".") -> str:
    """
    Extracts initials from a name string, taking into account:
      - Second names and patronyms (space-separated parts)
      - Compound names (hyphen-separated parts)
      - Consonant digraphs/sounds (e.g., 'Ch', 'Ll', 'Sch', 'Th')
    
    Parameters:
      - name: The string containing the name(s).
      - keep_compound_hyphen: If True, preserves hyphens in compound initials (e.g., J.-L.).
      - separator: The character placed after each initial (default is '.').
    """
    if not name or not isinstance(name, str):
        return ""

    # Define common digraphs/consonant clusters that represent a single sound/letter unit
    digraphs = {"ch", "ll", "sch", "th", "ph", "rh", "dz", "lj", "nj"}

    # Clean up extra whitespace
    name_clean = name.strip()
    
    # Split by whitespace to process each distinct name block (first name, second name, patronym)
    name_parts = name_clean.split()
    all_initials = []

    for part in name_parts:
        # Handle compound names connected by hyphens (e.g., "Jean-Luc", "Mary-Ann")
        subparts = part.split("-")
        part_initials = []
        
        for sub in subparts:
            sub_lower = sub.lower()
            matched_digraph = False
            
            # Check if the subpart starts with a known digraph (sorted by length descending for safety)
            for dg in sorted(digraphs, key=len, reverse=True):
                if sub_lower.startswith(dg):
                    # Capitalize the digraph properly (e.g., "Ch" or "Ll")
                    part_initials.append(sub[:len(dg)].capitalize())
                    matched_digraph = True
                    break
            
            # If no digraph matches, take the standard first letter
            if not matched_digraph and sub:
                part_initials.append(sub[0].upper())
        
        # Combine compound subpart initials with a hyphen or keep them flat
        if keep_compound_hyphen and len(part_initials) > 1:
            all_initials.append("-".join(part_initials))
        else:
            all_initials.extend(part_initials)

    # Join with the chosen separator and append a trailing separator if needed
    joined = separator.join(all_initials)
    return joined + (separator if all_initials and not joined.endswith(separator) else "")