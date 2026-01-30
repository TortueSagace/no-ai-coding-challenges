from time import perf_counter

def check_solution(s, p, proc, tmax, rmax):
    """
    s is the initial string (list of 0s and 1s)
    p the proposed subsequence (list of 1-indexed positions)
    """
    t0, r0 = perf_counter(), proc.memory_info().rss

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
    is_an_accurate_answer = (remaining == remaining[::-1])

    # Measure time and memory
    t1, r1 = perf_counter(), proc.memory_info().rss
    is_an_efficient_answer = (t1-t0 <= tmax, r1-r0 <= rmax)

    return (is_an_accurate_answer, is_an_efficient_answer[0], is_an_efficient_answer[1])
