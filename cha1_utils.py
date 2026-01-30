def check_solution(s, p):
    """
    s is the initial string (list of 0s and 1s)
    p the proposed subsequence (list of 1-indexed positions)
    """
    n = len(s)
    
    # Handle empty subsequence
    if not p:
        return s == s[::-1]  # s must be a palindrome
    
    # Check if indices are valid and in increasing order
    if not all(1 <= p[i] <= n for i in range(len(p))):
        return False
    if not all(p[i] < p[i+1] for i in range(len(p)-1)):
        return False
    
    # Extract the subsequence (convert to 0-indexed)
    subsequence = [s[idx-1] for idx in p]
    
    # Check if subsequence is non-decreasing (all 0s followed by all 1s)
    seen_one = False
    for val in subsequence:
        if val == 1:
            seen_one = True
        elif seen_one:  # val == 0 but we've already seen a 1
            return False
    
    # Get remaining string after removing p
    p_set = set(idx-1 for idx in p)  # convert to 0-indexed set
    remaining = [s[i] for i in range(n) if i not in p_set]
    
    # Check if remaining is a palindrome
    return remaining == remaining[::-1]
