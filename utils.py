from time import perf_counter
from psutil import Process
import os
from tqdm.notebook import tqdm

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
            result = my_solution(*sample)
        except Exception as e:
            print(f"❌  Runtime error at sample {i}: {e}")
            return False
        
        is_accurate, is_time_efficient, is_memory_efficient = check_solution(
            sample, result, proc, time_limit, memory_limit
        )
        
        if not is_accurate:
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
    
    for test_num, test_input in tqdm(enumerate(tests, 1)):
        try:
            result = my_solution(*test_input)
        except Exception as e:
            print(f"❌  Runtime error at test {test_num}: {e}")
            return False
        
        is_accurate, is_time_efficient, is_memory_efficient = check_solution(
            test_input, result, proc, time_limit, memory_limit
        )
        
        if not is_accurate:
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