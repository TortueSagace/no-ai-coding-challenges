"""
Utility functions for evaluating coding challenge solutions.

By Alexandre Le Mercier
"""

from time import perf_counter
from psutil import Process
import os
from tqdm.auto import tqdm

def get_trss(proc):
    """Get current time and RSS memory usage."""
    return perf_counter(), proc.memory_info().rss


def evaluate_on_samples(samples, my_solution, check_solution, time_limit, memory_limit):
    """
    Evaluate a solution on provided sample test cases.
    
    Parameters:
    -----------
    samples : list of tuples
        Each tuple contains the inputs for my_solution (e.g., (n, s) for challenge 1)
    my_solution : callable
        Function that takes unpacked sample inputs and returns the solution
    check_solution : callable
        Function with signature check_solution(sample, result, proc, tmax, rmax)
        Returns (is_accurate, is_time_efficient, is_memory_efficient)
    time_limit : float
        Maximum allowed time in seconds
    memory_limit : float
        Maximum allowed memory in bytes
    
    Returns:
    --------
    bool : True if all tests passed
    """
    proc = Process(os.getpid())
    all_passed = True
    
    for i, sample in enumerate(samples, 1):
        try:
            user_result = my_solution(*sample)
        except Exception as e:
            print(f"❌  Runtime error at sample {i}: {e}")
            return False
        
        check_result = check_solution(
            sample, user_result, proc, time_limit, memory_limit
        )
        
        # Unpack result (supports optional 4th element for custom error message)
        is_accurate, is_time_efficient, is_memory_efficient = check_result[:3]
        custom_message = check_result[3] if len(check_result) > 3 else None
        
        if not is_accurate:
            if custom_message:
                print(f"❌  {custom_message}")
            else:
                print(f"❌  Wrong answer at sample {i}")
            all_passed = False
            break
        elif not is_time_efficient:
            print(f"❌  Maximum time exceeded at sample {i}")
            all_passed = False
            break
        elif not is_memory_efficient:
            print(f"❌  Maximum memory exceeded at sample {i}")
            all_passed = False
            break
    
    if all_passed:
        print(f"✅  All {len(samples)} sample tests passed!")
    
    return all_passed


def internal_evaluation(test_file_path, my_solution, check_solution, parse_tests, time_limit, memory_limit):
    """
    Evaluate a solution on hidden test cases from a file.
    
    Parameters:
    -----------
    test_file_path : str
        Path to the test file
    my_solution : callable
        Function that takes test inputs and returns the solution
    check_solution : callable
        Function with signature check_solution(test_input, result, proc, tmax, rmax)
        Returns (is_accurate, is_time_efficient, is_memory_efficient)
    parse_tests : callable
        Function that parses the test file and returns a list of test inputs
        Signature: parse_tests(file_path) -> list of tuples
    time_limit : float
        Maximum allowed time in seconds
    memory_limit : float
        Maximum allowed memory in bytes
    
    Returns:
    --------
    bool : True if all tests passed
    """
    if not os.path.exists(test_file_path):
        print(f"❌  Test file not found: {test_file_path}")
        return False
    
    # Parse test cases using the challenge-specific parser
    tests = parse_tests(test_file_path)
    
    if not tests:
        print("❌  No test cases found in file")
        return False
    
    proc = Process(os.getpid())
    all_passed = True
    for test_num, test_input in tqdm(enumerate(tests, 1), total=len(tests)):
        try:
            user_result = my_solution(*test_input)
        except Exception as e:
            print(f"❌  Runtime error at test {test_num}: {e}")
            return False
        
        check_result = check_solution(
            test_input, user_result, proc, time_limit, memory_limit
        )
        
        # Unpack result (supports optional 4th element for custom error message)
        is_accurate, is_time_efficient, is_memory_efficient = check_result[:3]
        custom_message = check_result[3] if len(check_result) > 3 else None
        
        if not is_accurate:
            if custom_message:
                print(f"❌  {custom_message}")
            else:
                print(f"❌  Wrong answer at test {test_num}")
            all_passed = False
            break
        elif not is_time_efficient:
            print(f"❌  Maximum time exceeded at test {test_num}")
            all_passed = False
            break
        elif not is_memory_efficient:
            print(f"❌  Maximum memory exceeded at test {test_num}")
            all_passed = False
            break
    
    if all_passed:
        print(f"✅  All {len(tests)} tests passed!")
    
    return all_passed