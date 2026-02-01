# No-AI Coding Challenges

A series of programming puzzles designed to keep your brain sharp in a world where AI usually codes everything for you.

## Repository Structure

```
no-ai-coding-challenges/
├── README.md                           # This file
├── utils.py                            # Generic utilities (shared across all challenges)
├── cha1_utils.py                       # Challenge 1 specific utilities
├── cha1_tests.txt                      # Challenge 1 test cases (300 tests)
├── cha2_utils.py                       # Challenge 2 specific utilities
├── cha2_tests.txt                      # Challenge 2 test cases
└── ...
```

## Creating a New Challenge

When creating a new challenge (e.g., Challenge X), you need to create two files:

### 1. `chaX_utils.py` - Challenge-Specific Utilities

This file must implement the following functions:

#### Required Functions

```python
def get_input_size(test_input):
    """
    Extract the input size parameter (n) from the test input.
    Used for complexity analysis plotting.
    
    Parameters:
    -----------
    test_input : tuple
        The test input as parsed by parse_tests()
    
    Returns:
    --------
    int : The primary size parameter (n) of the input
    
    Example for a graph problem:
        test_input = (n, m, edges)  # n vertices, m edges
        return n  # or return n + m depending on what drives complexity
    """
    pass


def check_solution(test_input, result, proc, tmax, rmax):
    """
    Verify if the user's solution is correct.
    
    Parameters:
    -----------
    test_input : tuple
        The test input (e.g., (n, s) for challenge 1)
    result : any
        The return value from my_solution()
    proc : psutil.Process
        Process object for memory measurement (usually unused)
    tmax : float
        Maximum allowed time in seconds (usually unused, for legacy)
    rmax : float
        Maximum allowed memory in bytes (usually unused, for legacy)
    
    Returns:
    --------
    tuple : (is_accurate, is_time_efficient, is_memory_efficient, custom_message)
        - is_accurate: bool - True if solution is correct
        - is_time_efficient: bool - True (time measured externally now)
        - is_memory_efficient: bool - True (memory measured externally now)
        - custom_message: str or None - Custom error message for invalid output format
    
    Example:
        # Handle invalid return value
        if result is None:
            return (False, True, True, 'Invalid output format. Does your "my_solution" return X?')
        
        # Validate the solution
        is_correct = validate(test_input, result)
        return (is_correct, True, True, None)
    """
    pass


def parse_tests(file_path):
    """
    Parse the test file and return a list of test inputs.
    
    Parameters:
    -----------
    file_path : str
        Path to the chaX_tests.txt file
    
    Returns:
    --------
    list : List of tuples, where each tuple contains the inputs for my_solution()
    
    Example:
        # File format:
        # 300        <- number of test cases
        # 5          <- n for test 1
        # 01010      <- s for test 1
        # 3          <- n for test 2
        # ...
        
        tests = []
        for each test case:
            tests.append((n, s))  # Tuple of inputs for my_solution(n, s)
        return tests
    """
    pass


def parse_samples(sample_input):
    """
    Parse sample input string (from the notebook) into test cases.
    Same format as the test file but as a string.
    
    Parameters:
    -----------
    sample_input : str
        Multi-line string with test cases
    
    Returns:
    --------
    list : List of tuples (same format as parse_tests)
    """
    pass
```

#### Optional Functions (Recommended)

These functions improve the sample test output display:

```python
def format_input(sample):
    """
    Format a test input for display in the results table.
    
    Parameters:
    -----------
    sample : tuple
        The test input (e.g., (n, s) for challenge 1)
    
    Returns:
    --------
    str : Formatted string for display
    
    Example:
        n, s = sample
        return f"n={n}, s={''.join(str(x) for x in s)}"
    """
    pass


def format_output(result):
    """
    Format a solution output for display in the results table.
    
    Parameters:
    -----------
    result : any
        The return value from my_solution()
    
    Returns:
    --------
    str : Formatted string for display
    
    Example:
        if result is None:
            return "None"
        k, indices = result
        return f"k={k}, p={indices}"
    """
    pass
```

### 2. `chaX_tests.txt` - Test Cases File

Format:
```
<number_of_test_cases>
<test_1_line_1>
<test_1_line_2>
...
<test_2_line_1>
<test_2_line_2>
...
```

**Requirements:**
- At least 100 test cases recommended (300 is ideal)
- Cover edge cases (minimum/maximum values, empty inputs, etc.)
- Include various patterns (sorted, reverse sorted, random, etc.)
- Vary the input size `n` to enable meaningful complexity analysis

**Example for Challenge 1 (Beautiful String):**
```
300
3
010
3
001
5
00111
...
```

## Generic Utilities (`utils.py`)

The `utils.py` file provides shared functionality:

### `evaluate_on_samples(samples, my_solution, check_solution, time_limit, memory_limit, format_input=None, format_output=None)`
Evaluates the solution on provided sample test cases with a detailed results table.

**Parameters:**
- `format_input`: Optional function to format input for display: `format_input(sample) -> str`
- `format_output`: Optional function to format output for display: `format_output(result) -> str`

**Output Example:**
```
                         Sample Test Results                         
=====================================================================
   # │ Input           │ Output           │         Time │ Status    
─────┼─────────────────┼──────────────────┼──────────────┼───────────
   1 │ n=3, s=010      │ k=0, p=[]        │     260.0 μs │ ✅ Pass    
   2 │ n=3, s=001      │ k=2, p=[1, 2]    │      87.8 μs │ ✅ Pass    
   3 │ n=5, s=00111    │ k=2, p=[1, 2]    │      52.1 μs │ ✅ Pass    

============================================================
✅  All 3 sample tests passed!
```

### `internal_evaluation(test_file_path, my_solution, check_solution, parse_tests, time_limit, memory_limit, get_input_size=None, plot=True, plot_title="", show_estimation=True)`
Evaluates on hidden test cases with optional complexity analysis plotting.

**Parameters:**
- `get_input_size`: Function to extract n from test_input (enables plotting)
- `plot`: Whether to show complexity analysis graphs
- `plot_title`: Title prefix for the complexity plot
- `show_estimation`: Whether to show complexity estimation (default: True). Set to `False` when n range is too small for reliable estimation (e.g., n ≤ 100)

## Notebook Template

```python
# Cell 1: Setup
import sys, os

if not os.path.exists('.git') and not os.path.exists('no-ai-coding-challenges'):
    !git clone https://github.com/YOUR_USERNAME/no-ai-coding-challenges.git -q

repo_path = 'no-ai-coding-challenges'
if os.path.exists(repo_path) and repo_path not in sys.path:
    sys.path.insert(0, repo_path)

from utils import *
from chaX_utils import *

# Cell 2: Sample setup
sample_input = """...."""

TIME_LIMIT = 1
MEMORY_LIMIT = 256e6

samples = parse_samples(sample_input)
print(f"Loaded {len(samples)} sample test cases.")

# Cell 3: User solution
def my_solution(param1, param2, ...):
    # User implements their solution here
    pass

# Cell 4: Sample evaluation (with optional formatting)
evaluate_on_samples(
    samples, my_solution, check_solution, TIME_LIMIT, MEMORY_LIMIT,
    format_input=format_input,   # Optional: from chaX_utils
    format_output=format_output  # Optional: from chaX_utils
)

# Cell 5: Full evaluation
test_file_path = 'no-ai-coding-challenges/chaX_tests.txt'

internal_evaluation(
    test_file_path, my_solution, check_solution, parse_tests,
    TIME_LIMIT, MEMORY_LIMIT,
    get_input_size=get_input_size,
    plot_title='Challenge X Name',
    show_estimation=True  # Set to False if n range is too small (e.g., n ≤ 100)
)
```

## Complexity Analysis

When `get_input_size` is provided, the evaluation automatically:
1. Measures execution time and memory for each test
2. Groups measurements by input size `n`
3. Fits various complexity functions (O(1), O(log n), O(n), O(n log n), O(n²), O(n³), O(2ⁿ))
4. Plots the results with the best-fit curve
5. Reports estimated time and space complexity

## Collapsible Content (Solutions, Hints)

To hide solutions or hints by default, use HTML `<details>` and `<summary>` tags in markdown cells:

```html
<details>
<summary><strong>💡 Click to reveal Solution Explanation</strong></summary>

<div style="color: black; background-color: #cce5ff; padding: 10px; border-left: 5px solid #3399ff; border-radius: 5px; margin-top: 10px;">
    Your solution explanation here...
    
    <strong>Strategy:</strong>
    <ol>
        <li>Step 1</li>
        <li>Step 2</li>
    </ol>
</div>

</details>
```

This renders as a collapsed element that users must click to expand, keeping solutions hidden until explicitly requested.

**Color schemes for different box types:**
- **Blue (info/solution):** `background-color: #cce5ff; border-left: 5px solid #3399ff;`
- **Yellow (warning/hint):** `background-color: #fff3cd; border-left: 5px solid #ffc107;`
- **Red (important):** `background-color: #ffcccc; border-left: 5px solid #ff3333;`
- **Green (success):** `background-color: #d4edda; border-left: 5px solid #28a745;`

## Tips for Challenge Creators

1. **Input Size Range**: Ensure `n` varies enough for meaningful complexity analysis (e.g., 1-10, 1-100, 1-1000)

2. **Test Distribution**: Have multiple test cases for each value of `n` to get stable averages

3. **Edge Cases**: Always include:
   - Minimum size (n=1)
   - Maximum size
   - Special patterns (all same values, alternating, sorted, etc.)

4. **Validation**: Test your `check_solution` with both correct and incorrect solutions

5. **Error Messages**: Provide helpful custom error messages for common mistakes

6. **Complexity Estimation**: Set `show_estimation=False` when n range is too small (n ≤ 100) for reliable empirical complexity analysis. The constant overhead (~50μs) dominates at small n, making all algorithms appear O(1). For reliable estimation, n should span 2-3 orders of magnitude (e.g., 10 to 10,000).

## License

MIT License - Feel free to use and adapt for educational purposes.