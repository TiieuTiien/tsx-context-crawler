import os
import sys
import fnmatch

DEFAULT_RECURSION_DEPTH = 3

def should_ignore(path, ignore_patterns):
    """
    Checks if a given path should be ignored based on the provided ignore patterns.

    Args:
        path (str): The path to check.
        ignore_patterns (list): A list of ignore patterns from .gitignore.

    Returns:
        bool: True if the path should be ignored, False otherwise.
    """
    for pattern in ignore_patterns:
        if fnmatch.fnmatch(path, pattern) or fnmatch.fnmatch(os.path.basename(path), pattern):
            return True
    return False

def read_gitignore(directory):
    """
    Reads the .gitignore file in the given directory and returns a list of patterns.

    Args:
        directory (str): The directory containing the .gitignore file.

    Returns:
        list: A list of ignore patterns, or an empty list if .gitignore is not found.
    """
    gitignore_path = os.path.join(directory, ".gitignore")
    if os.path.exists(gitignore_path):
        with open(gitignore_path, 'r', encoding='utf-8') as f:
            patterns = [line.strip() for line in f if line.strip() and not line.startswith("#")]
        return patterns
    return []

def crawl_tsx_and_save_with_gitignore(directory, output_file="tsx_content.txt", max_depth=None):
    """
    Crawls through a directory recursively up to a specified depth, finds all .tsx files,
    respects .gitignore, and saves their names and content into a text file.

    Args:
        directory (str): The path to the directory to crawl.
        output_file (str, optional): The name of the output text file.
            Defaults to "tsx_content.txt".
        max_depth (int, optional): The maximum recursion depth. If None, crawls fully.
    """
    ignore_patterns = read_gitignore(directory)

    def _crawl(current_dir, depth):
        if max_depth is not None and depth > max_depth:
            return

        try:
            for item in os.listdir(current_dir):
                item_path = os.path.join(current_dir, item)
                relative_path = os.path.relpath(item_path, directory)

                if os.path.isfile(item_path) and item.endswith(".tsx"):
                    if not should_ignore(relative_path, ignore_patterns):
                        try:
                            with open(item_path, 'r', encoding='utf-8') as infile:
                                content = infile.read()
                                outfile.write(f"Filename: {relative_path}\n")
                                outfile.write(f"Content:\n{content}\n")
                                outfile.write("-" * 40 + "\n")  # Separator
                            print(f"Processed: {relative_path}")
                        except Exception as e:
                            print(f"Error reading file {item_path}: {e}")
                    else:
                        print(f"Ignored: {relative_path} (matches .gitignore)")
                elif os.path.isdir(item_path) and not should_ignore(relative_path, ignore_patterns):
                    _crawl(item_path, depth + 1)

        except Exception as e:
            print(f"Error accessing directory {current_dir}: {e}")

    try:
        with open(output_file, 'w', encoding='utf-8') as outfile:
            _crawl(directory, 0)
        print(f"\nSuccessfully saved content of relevant .tsx files to: {output_file}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    target_directory = os.getcwd()
    max_recursion_depth = DEFAULT_RECURSION_DEPTH
    crawl_full = False

    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            arg = arg.strip('"').strip("'")
            if arg == "--full":
                crawl_full = True
                max_recursion_depth = None
            else:
                target_directory = arg
                try:
                    # If a number is provided as the directory, it's likely a mistake
                    int(target_directory)
                except ValueError:
                    pass # It's likely a directory path
                else:
                    print(f"Warning: '{target_directory}' looks like a number and is being treated as the target directory.")

    if crawl_full:
        print(f"Crawling directory: {target_directory} with full recursion.")
    else:
        print(f"Crawling directory: {target_directory} with a maximum depth of {max_recursion_depth}.")

    crawl_tsx_and_save_with_gitignore(target_directory, max_depth=max_recursion_depth)