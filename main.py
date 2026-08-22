import os
import tempfile
from pathlib import Path


def _write_output_atomically(output_path, lines):
    """Replace ``output_path`` only after the complete output is written."""
    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=output_path.parent,
            prefix=f".{output_path.name}.",
            suffix=".tmp",
            delete=False,
        ) as temporary_file:
            temporary_path = Path(temporary_file.name)
            for line in lines:
                temporary_file.write(line + "\n")
            temporary_file.flush()
            os.fsync(temporary_file.fileno())
        os.replace(temporary_path, output_path)
    except BaseException:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)
        raise


def run(rule, no_steps=100, *, output_dir=None):
    """Run a one-dimensional cellular automaton for ``no_steps`` generations.

    ``rule`` is an eight-bit Wolfram rule number and ``no_steps`` must be a
    positive integer. ``output_dir`` optionally selects the directory for the
    generated output and is keyword-only to preserve positional compatibility.
    Validate these public inputs before creating output so invalid requests
    fail without partial files or misleading output.
    """
    if isinstance(rule, bool) or not isinstance(rule, int):
        raise TypeError("rule must be an integer from 0 through 255")
    if not 0 <= rule <= 255:
        raise ValueError("rule must be an integer from 0 through 255")
    if isinstance(no_steps, bool) or not isinstance(no_steps, int):
        raise TypeError("no_steps must be a positive integer")
    if no_steps <= 0:
        raise ValueError("no_steps must be a positive integer")

    # Define the initial state, typically a single active cell in the middle
    initial_state = [0] * no_steps * 2
    initial_state[no_steps] = 1

    # Define the rule as an 8-bit binary number, e.g., 30 for Rule 30
    binary_rule = f'{rule:08b}'

    # Create a dictionary to map neighborhood patterns to new cell states
    rule_dict = {}
    count_dict = {}
    for pattern in range(7, -1, -1):
        rule_dict[format(pattern, '03b')] = binary_rule[7 - pattern]
        count_dict[format(pattern, '03b')] = 0

    # Initialize the list to store the automaton's history
    automaton_history = [initial_state]

    # Generate the automaton's history
    for _ in range(no_steps - 1):
        current_state = automaton_history[-1]
        new_state = [0] * no_steps * 2

        # Apply the rule to determine the new state
        for i in range(1, no_steps * 2 - 1):
            neighborhood = ''.join(map(str, current_state[i - 1:i + 2]))
            new_state[i] = int(rule_dict.get(neighborhood, '0'))
            count_dict[neighborhood] += 1

        automaton_history.append(new_state)

    # Write the automaton's history to a text file with leading zeros
    output_dir = Path("output") if output_dir is None else Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_lines = []
    for state in automaton_history:
        line = ''.join(map(str, state))
        line = line.replace('0', ' ')
        line = line.replace('1', '■')
        line = line.rjust(no_steps, '0')
        print(line)
        output_lines.append(line)
    _write_output_atomically(output_dir / f"rule_{rule}_output.txt", output_lines)

    #print(count_dict)
    return count_dict

if __name__ == "__main__":
    run(30, 430)

# Example usage:
# for i in range(1, 256):
#     count_dict = run(i, 200)  # Run Rule for n steps and store the result in "rule_<ruleNo>_output.txt"
#     uses_all_conditions = True
#     for key in count_dict:
#         if count_dict[key] == 0:
#             uses_all_conditions = False

#     if uses_all_conditions:
#         print(f"RULE {i}")
