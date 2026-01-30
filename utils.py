from time import perf_counter
import sys, os
from io import StringIO
from psutil import Process

def get_trss(proc):
    return perf_counter(), proc.memory_info().rss

def rigid_evaluation_on_provided_examples(cap, sample_output, proc, t0, r0, tmax, rmax):
    correct = True
    try:
        assert len(cap.stdout.strip()) > 0, "❌  no output found! Did you forget '%%capture cap'?"
        assert cap.stdout.strip() == sample_output.strip(), "❌  output differs!"
        print("✅  matches expected output")
    except AssertionError as e:
        print(e)
        correct = False

    t1, r1 = get_trss(proc)

    print(f"Time (sec): {t1-t0:>10.3e}")
    print(f"RSS (B): {r1-r0:>13.3e}")
    try:
        assert (t1-t0 <= tmax and r1-r0 <= rmax), "❌  your code isn't efficient enough! Check time/space limits."
        print("✅  efficient enough")
    except AssertionError as e:
        print(e)
        correct = False

    return correct

def internal_evaluation(test_file_path, my_solution, check_solution, TIME_LIMIT, MEMORY_LIMIT):

    # Read hidden test cases from git repository
    test_file_path = 'no-ai-coding-challenges/cha1_tests.txt'

    if not os.path.exists(test_file_path):
        print("❌  Test file not found! Please ensure the git repository contains 'cha1_tests.txt'")
    else:
        with open(test_file_path, 'r') as f:
            hidden_tests = f.read()
        
        # Parse the input to get test cases
        input_lines = hidden_tests.strip().split('\n')
        t = int(input_lines[0])
        
        # Prepare input for my_solution
        sys.stdin = StringIO(hidden_tests)
        
        # Capture output
        output_capture = StringIO()
        old_stdout = sys.stdout
        sys.stdout = output_capture
        
        # Run user's solution
        proc = Process(os.getpid())
        try:
            my_solution()
            sys.stdout = old_stdout
        except Exception as e:
            sys.stdout = old_stdout
            print(f"❌  Runtime error: {e}")
            raise
        
        # Parse outputs
        output_lines = output_capture.getvalue().strip().split('\n')
        output_idx = 0
        
        # Parse inputs to check against
        input_idx = 1
        all_passed = True
        
        for test_num in range(1, t + 1):
            # Read the input for this test
            n = int(input_lines[input_idx])
            s = [int(c) for c in input_lines[input_idx + 1].strip()]
            input_idx += 2
            
            # Read the output for this test
            try:
                k = int(output_lines[output_idx])
                output_idx += 1
                
                if k == 0:
                    p = []
                    # Skip empty line if present
                    if output_idx < len(output_lines) and output_lines[output_idx].strip() == '':
                        output_idx += 1
                else:
                    p = list(map(int, output_lines[output_idx].split()))
                    output_idx += 1
            except Exception as e:
                print(f"❌  Wrong answer at test {test_num} (output parsing error: {e})")
                all_passed = False
                break
            
            # Check solution
            is_accurate, is_time_efficient, is_memory_efficient = check_solution(s, p, proc, TIME_LIMIT, MEMORY_LIMIT)
            
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
            print("✅  All tests passed!")