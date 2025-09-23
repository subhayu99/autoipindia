from itertools import product


SIMILAR_LOOKING_NUMBERS = {
    0: [3, 8],
    1: [4, 7],
    2: [7],
    3: [0, 8],
    4: [1, 7],
    5: [6],
    6: [5],
    7: [1, 4],
    8: [0, 3],
    9: [5, 3],
}

def generate_combinations(code):
    """
    Generate all possible combinations of a code based on similar-looking numbers.
    
    Args:
        code (str): The original code (e.g., "881558")
    
    Returns:
        list: All possible combinations including the original
    """
    # Convert code to list of integers
    digits = [int(d) for d in str(code)]
    
    # For each digit, create a list of possible alternatives (including the original)
    possibilities = []
    for digit in digits:
        # Start with the original digit
        alternatives = [digit]
        # Add similar looking numbers if they exist
        if digit in SIMILAR_LOOKING_NUMBERS:
            alternatives.extend(SIMILAR_LOOKING_NUMBERS[digit])
        # Remove duplicates while preserving order
        alternatives = list(dict.fromkeys(alternatives))
        possibilities.append(alternatives)
    
    # Generate all combinations using cartesian product
    combinations = []
    for combination in product(*possibilities):
        combinations.append(''.join(map(str, combination)))
    
    return combinations

def generate_combinations_sorted(code, max_combinations=None):
    """
    Generate combinations sorted by likelihood (original first, then by number of changes).
    
    Args:
        code (str): The original code
        max_combinations (int, optional): Maximum number of combinations to return
    
    Returns:
        list: Sorted combinations with original first
    """
    original = str(code)
    combinations = generate_combinations(code)
    
    # Calculate "distance" from original (number of different digits)
    def distance_from_original(combo):
        return sum(1 for i, (a, b) in enumerate(zip(original, combo)) if a != b)
    
    # Sort by distance from original (0 = original, 1 = one change, etc.)
    combinations.sort(key=distance_from_original)
    
    if max_combinations:
        return combinations[:max_combinations]
    
    return combinations


# Additional utility functions
def get_digit_alternatives(digit):
    """Get all alternatives for a specific digit"""
    digit = int(digit)
    alternatives = [digit]
    if digit in SIMILAR_LOOKING_NUMBERS:
        alternatives.extend(SIMILAR_LOOKING_NUMBERS[digit])
    return list(dict.fromkeys(alternatives))

def analyze_code_complexity(code):
    """Analyze how many combinations a code will generate"""
    digits = [int(d) for d in str(code)]
    total_combinations = 1
    
    print(f"Code analysis for: {code}")
    print("-" * 30)
    
    for i, digit in enumerate(digits):
        alternatives = get_digit_alternatives(digit)
        alt_count = len(alternatives)
        total_combinations *= alt_count
        
        print(f"Position {i+1}: {digit} → {alternatives} ({alt_count} options)")
    
    print(f"\nTotal combinations: {total_combinations}")
    return total_combinations


# Example usage
if __name__ == "__main__":
    code = "881558"
    
    print(f"Original code: {code}")
    print(f"Number of digits: {len(code)}")
    
    # Generate all combinations
    all_combinations = generate_combinations(code)
    print(f"\nTotal combinations: {len(all_combinations)}")
    
    # Show first 20 combinations
    print("\nFirst 20 combinations:")
    for i, combo in enumerate(all_combinations[:20]):
        print(f"{i+1:2d}. {combo}")
    
    if len(all_combinations) > 20:
        print(f"... and {len(all_combinations) - 20} more")
    
    print("\n" + "="*50)
    
    # Generate sorted combinations (most likely first)
    sorted_combinations = generate_combinations_sorted(code, max_combinations=30)
    print("\nTop 30 most likely combinations (sorted by similarity to original):")
    
    original = str(code)
    for i, combo in enumerate(sorted_combinations):
        # Calculate how many digits are different
        diff_count = sum(1 for a, b in zip(original, combo) if a != b)
        if diff_count == 0:
            print(f"{i+1:2d}. {combo} ← ORIGINAL")
        else:
            print(f"{i+1:2d}. {combo} ({diff_count} changes)")

    print("\n" + "="*50)
    print("CODE COMPLEXITY ANALYSIS")
    print("="*50)
    analyze_code_complexity(code)
