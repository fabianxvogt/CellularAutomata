def run(rule, no_steps=100):
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
    with open(f'output/rule_{rule}_output.txt', 'w') as file:
        for state in automaton_history:
            line = ''.join(map(str, state))
            line = line.replace('0', ' ')
            line = line.replace('1', '■')
            line = line.rjust(no_steps, '0')
            print(line)
            file.write(line + '\n')

    #print(count_dict)
    return count_dict

count_dict = run(30, 430)
# Example usage:
# for i in range(1, 257):
#     count_dict = run(i, 200)  # Run Rule for n steps and store the result in "rule_<ruleNo>_output.txt"
#     uses_all_conditions = True
#     for key in count_dict:
#         if count_dict[key] == 0:
#             uses_all_conditions = False

#     if uses_all_conditions:
#         print(f"RULE {i}")
