from time import perf_counter

def check_solution(test_input, result, proc, tmax, rmax):
    """
    Check if the solution is correct for the Beautiful String problem.
    
    Parameters:
    -----------
    test_input : tuple
        (n, s) where n is the length and s is the binary string as a list of 0s and 1s
    result : tuple
        (k, p) where k is the subsequence length and p is the list of 1-indexed positions
    proc : psutil.Process
        Process object for memory measurement
    tmax : float
        Maximum allowed time in seconds
    rmax : float
        Maximum allowed memory in bytes
    
    Returns:
    --------
    tuple : (is_accurate, is_time_efficient, is_memory_efficient)
    """
    t0, r0 = perf_counter(), proc.memory_info().rss
    
    n, s = test_input
    k, p = result
    
    # Handle empty subsequence
    if k == 0 or not p:
        is_accurate = (s == s[::-1])  # s must already be a palindrome
    else:
        # Check if k matches length of p
        if k != len(p):
            is_accurate = False
        # Check if indices are valid and in increasing order
        elif not all(1 <= p[i] <= n for i in range(len(p))):
            is_accurate = False
        elif not all(p[i] < p[i+1] for i in range(len(p)-1)):
            is_accurate = False
        else:
            # Extract the subsequence (convert to 0-indexed)
            subsequence = [s[idx-1] for idx in p]
            
            # Check if subsequence is non-decreasing (all 0s followed by all 1s)
            seen_one = False
            is_non_decreasing = True
            for val in subsequence:
                if val == 1:
                    seen_one = True
                elif seen_one:  # val == 0 but we've already seen a 1
                    is_non_decreasing = False
                    break
            
            if not is_non_decreasing:
                is_accurate = False
            else:
                # Get remaining string after removing p
                p_set = set(idx-1 for idx in p)  # convert to 0-indexed set
                remaining = [s[i] for i in range(n) if i not in p_set]
                
                # Check if remaining is a palindrome
                is_accurate = (remaining == remaining[::-1])
    
    # Measure time and memory
    t1, r1 = perf_counter(), proc.memory_info().rss
    is_time_efficient = (t1 - t0 <= tmax)
    is_memory_efficient = (r1 - r0 <= rmax)
    
    return (is_accurate, is_time_efficient, is_memory_efficient)


def parse_tests(file_path):
    """
    Parse the test file for Challenge 1 (Beautiful String).
    
    File format:
    - First line: number of test cases t
    - For each test case:
        - Line with n (length of string)
        - Line with binary string s
    
    Parameters:
    -----------
    file_path : str
        Path to the test file
    
    Returns:
    --------
    list : List of tuples (n, s) where s is a list of integers (0s and 1s)
    """
    with open(file_path, 'r') as f:
        lines = f.read().strip().split('\n')
    
    t = int(lines[0])
    tests = []
    idx = 1
    
    for _ in range(t):
        n = int(lines[idx])
        s = [int(c) for c in lines[idx + 1].strip()]
        tests.append((n, s))
        idx += 2
    
    return tests