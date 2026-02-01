from time import perf_counter
from psutil import Process
from tqdm.auto import tqdm
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict
import os


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
        Returns (is_accurate, is_time_efficient, is_memory_efficient, custom_message)
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


def _fit_complexity(n_values, measurements):
    """
    Fit various complexity functions to the measurements and find the best match.
    
    Returns:
    --------
    tuple : (best_name, best_func, best_params, all_results)
    """
    n = np.array(n_values, dtype=float)
    y = np.array(measurements, dtype=float)
    
    # Handle edge case: all measurements are zero or constant
    if np.std(y) < 1e-10:
        return ("O(1)", lambda n: np.ones_like(n), (np.mean(y), 0), [])
    
    # Avoid division by zero and log of zero
    n_safe = np.maximum(n, 1)
    
    # Calculate coefficient of variation to check if data is essentially constant
    cv = np.std(y) / (np.mean(y) + 1e-10)
    
    # Define complexity functions: (name, transform_function)
    complexities = [
        ("O(1)", lambda n: np.ones_like(n)),
        ("O(log n)", lambda n: np.log2(np.maximum(n, 1))),
        ("O(n)", lambda n: n),
        ("O(n log n)", lambda n: n * np.log2(np.maximum(n, 1))),
        ("O(n²)", lambda n: n ** 2),
        ("O(n³)", lambda n: n ** 3),
        ("O(2ⁿ)", lambda n: 2 ** np.minimum(n, 30)),  # Cap to avoid overflow
    ]
    
    results = []
    
    for name, func in complexities:
        try:
            x = func(n_safe)
            
            # For O(1), we fit y = constant
            if name == "O(1)":
                mean_y = np.mean(y)
                y_pred = np.full_like(y, mean_y)
                ss_res = np.sum((y - y_pred) ** 2)
                ss_tot = np.sum((y - mean_y) ** 2)
                # R² for constant model is 0 by definition (unless data is constant)
                r2 = 0.0 if ss_tot > 1e-10 else 1.0
                results.append((name, func, (mean_y, 0), r2))
                continue
            
            # Skip if all x values are the same (can't fit)
            if np.std(x) < 1e-10:
                continue
            
            # Linear regression: y = a * x + b
            # Using least squares
            A = np.vstack([x, np.ones(len(x))]).T
            coeffs, residuals, rank, s = np.linalg.lstsq(A, y, rcond=None)
            a, b = coeffs
            
            # Only consider positive scaling factors for non-constant models
            if a <= 0:
                continue
            
            # Calculate R² score
            y_pred = a * x + b
            ss_res = np.sum((y - y_pred) ** 2)
            ss_tot = np.sum((y - np.mean(y)) ** 2)
            
            if ss_tot < 1e-10:
                r2 = 1.0 if ss_res < 1e-10 else 0.0
            else:
                r2 = 1 - (ss_res / ss_tot)
            
            results.append((name, func, (a, b), r2))
        except Exception:
            continue
    
    if not results:
        return ("O(1)", lambda n: np.ones_like(n), (np.mean(y), 0), [])
    
    # Sort by R² score (descending)
    results.sort(key=lambda x: x[3], reverse=True)
    
    # If the best R² is very low (< 0.5) and data has low coefficient of variation,
    # it's likely O(1) with noise
    best = results[0]
    if best[3] < 0.5 and cv < 0.3:
        # Find O(1) in results or return it
        for r in results:
            if r[0] == "O(1)":
                return r
        return ("O(1)", lambda n: np.ones_like(n), (np.mean(y), 0), results)
    
    return (best[0], best[1], best[2], results)


def _plot_complexity_analysis(time_by_n, memory_by_n, title_prefix="", show_estimation=True):
    """
    Create a beautiful plot showing time and memory complexity analysis.
    
    Parameters:
    -----------
    time_by_n : dict
        Dictionary mapping n -> list of execution times
    memory_by_n : dict
        Dictionary mapping n -> list of memory usages
    title_prefix : str
        Optional prefix for the plot title
    show_estimation : bool
        Whether to show complexity estimation annotations (default: True)
    """
    # Set up the style - use a style that's likely to be available
    try:
        plt.style.use('seaborn-v0_8-whitegrid')
    except OSError:
        try:
            plt.style.use('seaborn-whitegrid')
        except OSError:
            pass  # Use default style
    
    # Create figure with two subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    fig.patch.set_facecolor('white')
    
    # Color scheme
    color_primary = '#2E86AB'      # Blue
    color_secondary = '#A23B72'    # Pink/Magenta
    color_fit = '#F18F01'          # Orange
    color_fit2 = '#C73E1D'         # Red
    
    # Prepare data
    n_values = sorted(time_by_n.keys())
    
    # Calculate averages and std
    avg_times = [np.mean(time_by_n[n]) * 1e6 for n in n_values]  # Convert to microseconds
    std_times = [np.std(time_by_n[n]) * 1e6 for n in n_values]
    avg_memory = [np.mean(memory_by_n[n]) / 1024 for n in n_values]  # Convert to KB
    std_memory = [np.std(memory_by_n[n]) / 1024 for n in n_values]
    
    # Fit complexity curves
    time_fit = _fit_complexity(n_values, avg_times)
    memory_fit = _fit_complexity(n_values, avg_memory)
    
    # Generate smooth curve for plotting
    n_smooth = np.linspace(min(n_values), max(n_values), 100)
    
    # ==================== TIME PLOT ====================
    ax1.errorbar(n_values, avg_times, yerr=std_times, fmt='o', 
                 color=color_primary, markersize=8, capsize=5, capthick=2,
                 label='Measured time', ecolor=color_primary, alpha=0.7)
    
    # Plot fitted curve (only if show_estimation is True)
    if show_estimation:
        a, b = time_fit[2]
        if time_fit[0] == "O(1)":
            # Horizontal line for O(1)
            ax1.axhline(y=a, color=color_fit, linestyle='--', linewidth=2.5,
                        label=f'Fitted: {time_fit[0]}')
        elif a > 0:
            y_fit = a * time_fit[1](n_smooth) + b
            ax1.plot(n_smooth, y_fit, '--', color=color_fit, linewidth=2.5,
                     label=f'Fitted: {time_fit[0]}')
    
    ax1.set_xlabel('Input Size (n)', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Execution Time (μs)', fontsize=12, fontweight='bold')
    ax1.set_title('Time Complexity Analysis', fontsize=14, fontweight='bold', pad=10)
    ax1.legend(loc='upper left', fontsize=10)
    ax1.set_ylim(bottom=0)  # Start from 0
    
    # Add complexity annotation (only if show_estimation is True)
    if show_estimation:
        ax1.annotate(f'Estimated: {time_fit[0]}', 
                     xy=(0.95, 0.05), xycoords='axes fraction',
                     fontsize=12, fontweight='bold', color=color_fit,
                     ha='right', va='bottom',
                     bbox=dict(boxstyle='round,pad=0.3', facecolor='white', 
                              edgecolor=color_fit, alpha=0.9))
    
    # ==================== MEMORY PLOT ====================
    # Check if memory data is all zeros
    all_zero_memory = all(m == 0 for m in avg_memory)
    
    if all_zero_memory:
        if show_estimation:
            msg = 'Memory changes too small\nto measure accurately\n\nEstimated: O(1)'
        else:
            msg = 'Memory changes too small\nto measure accurately'
        ax2.text(0.5, 0.5, msg, 
                 transform=ax2.transAxes, fontsize=14, ha='center', va='center',
                 bbox=dict(boxstyle='round,pad=0.5', facecolor='white', 
                          edgecolor=color_secondary, alpha=0.9),
                 color=color_secondary)
        ax2.set_xlim(min(n_values) - 0.5, max(n_values) + 0.5)
        memory_fit = ("O(1)", lambda n: np.ones_like(n), (0, 0), [])
    else:
        ax2.errorbar(n_values, avg_memory, yerr=std_memory, fmt='s',
                     color=color_secondary, markersize=8, capsize=5, capthick=2,
                     label='Measured memory', ecolor=color_secondary, alpha=0.7)
        
        # Plot fitted curve (only if show_estimation is True)
        if show_estimation:
            a, b = memory_fit[2]
            if memory_fit[0] == "O(1)":
                ax2.axhline(y=a, color=color_fit2, linestyle='--', linewidth=2.5,
                            label=f'Fitted: {memory_fit[0]}')
            elif a > 0:
                y_fit = a * memory_fit[1](n_smooth) + b
                ax2.plot(n_smooth, y_fit, '--', color=color_fit2, linewidth=2.5,
                         label=f'Fitted: {memory_fit[0]}')
        
        ax2.legend(loc='upper left', fontsize=10)
        ax2.set_ylim(bottom=0)
        
        # Add complexity annotation (only if show_estimation is True)
        if show_estimation:
            ax2.annotate(f'Estimated: {memory_fit[0]}', 
                         xy=(0.95, 0.05), xycoords='axes fraction',
                         fontsize=12, fontweight='bold', color=color_fit2,
                         ha='right', va='bottom',
                         bbox=dict(boxstyle='round,pad=0.3', facecolor='white', 
                                  edgecolor=color_fit2, alpha=0.9))
    
    ax2.set_xlabel('Input Size (n)', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Memory Usage (KB)', fontsize=12, fontweight='bold')
    ax2.set_title('Space Complexity Analysis', fontsize=14, fontweight='bold', pad=10)
    
    # Overall title
    main_title = "Complexity Analysis"
    if title_prefix:
        main_title = f"{title_prefix} - {main_title}"
    fig.suptitle(main_title, fontsize=16, fontweight='bold', y=1.02)
    
    plt.tight_layout()
    plt.show()
    
    return time_fit[0], memory_fit[0]


def internal_evaluation(test_file_path, my_solution, check_solution, parse_tests,
                        time_limit, memory_limit, get_input_size=None, plot=True,
                        plot_title="", show_estimation=True):
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
        Returns (is_accurate, is_time_efficient, is_memory_efficient, custom_message)
    parse_tests : callable
        Function that parses the test file and returns a list of test inputs
        Signature: parse_tests(file_path) -> list of tuples
    time_limit : float
        Maximum allowed time in seconds
    memory_limit : float
        Maximum allowed memory in bytes
    get_input_size : callable, optional
        Function that extracts the size parameter (n) from test_input for plotting
        Signature: get_input_size(test_input) -> int
        If None, plotting is disabled
    plot : bool
        Whether to plot complexity analysis (default: True)
        Requires get_input_size to be provided
    plot_title : str
        Optional title prefix for the complexity plot
    show_estimation : bool
        Whether to show complexity estimation on the plot (default: True)
        Set to False when n range is too small for reliable estimation
    
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
    
    # For complexity analysis
    time_by_n = defaultdict(list)
    memory_by_n = defaultdict(list)
    
    for test_num, test_input in tqdm(enumerate(tests, 1), total=len(tests)):
        # Measure execution time
        t_start = perf_counter()
        mem_before = proc.memory_info().rss
        
        try:
            user_result = my_solution(*test_input)
        except Exception as e:
            print(f"\n❌  Runtime error at test {test_num}: {e}")
            return False
        
        t_end = perf_counter()
        mem_after = proc.memory_info().rss
        
        # Record metrics for complexity analysis
        if get_input_size is not None:
            n = get_input_size(test_input)
            time_by_n[n].append(t_end - t_start)
            memory_by_n[n].append(max(0, mem_after - mem_before))
        
        check_result = check_solution(
            test_input, user_result, proc, time_limit, memory_limit
        )
        
        # Unpack result (supports optional 4th element for custom error message)
        is_accurate, is_time_efficient, is_memory_efficient = check_result[:3]
        custom_message = check_result[3] if len(check_result) > 3 else None
        
        if not is_accurate:
            if custom_message:
                print(f"\n❌  {custom_message}")
            else:
                print(f"\n❌  Wrong answer at test {test_num}")
            all_passed = False
            break
        elif not is_time_efficient:
            print(f"\n❌  Maximum time exceeded at test {test_num}")
            all_passed = False
            break
        elif not is_memory_efficient:
            print(f"\n❌  Maximum memory exceeded at test {test_num}")
            all_passed = False
            break
    
    if all_passed:
        print(f"✅  All {len(tests)} tests passed!")
        
        # Plot complexity analysis if enabled and we have data
        if plot and get_input_size is not None and time_by_n:
            time_complexity, space_complexity = _plot_complexity_analysis(
                time_by_n, memory_by_n, title_prefix=plot_title,
                show_estimation=show_estimation
            )
            if show_estimation:
                print(f"\n📊 Estimated Time Complexity: {time_complexity}")
                print(f"📊 Estimated Space Complexity: {space_complexity}")
    
    return all_passed