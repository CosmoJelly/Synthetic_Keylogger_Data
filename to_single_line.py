def multiline_to_single_line(text):
    # Split lines, strip each line, and join with a single space
    return ' '.join(line.strip() for line in text.strip().splitlines())

# Example usage:
if __name__ == "__main__":
    print("Paste your text below (press Ctrl+D or Ctrl+Z to finish):\n")
    try:
        # Read multi-line input from stdin
        import sys
        input_text = sys.stdin.read()
    except KeyboardInterrupt:
        input_text = ""

    single_line = multiline_to_single_line(input_text)
    print("\n--- Single Line Output ---\n")
    print(single_line)