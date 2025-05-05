import argparse
import os
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
    # .gitignore patterns can apply to the path relative to the gitignore file
    # or sometimes just the filename. Checking both relative_path and basename is a reasonable approach.
    for pattern in ignore_patterns:
        # Using fnmatch.fnmatchcase for case-sensitive matching on case-sensitive file systems
        # and case-insensitive on case-insensitive file systems, which is closer to Git's behavior.
        # However, fnmatch doesn't have a simple case-insensitive mode across all systems.
        # Sticking with fnmatch for simplicity as originally used, but be aware of case sensitivity nuances.
        if fnmatch.fnmatch(path, pattern) or fnmatch.fnmatch(os.path.basename(path), pattern):
            return True
    return False

def read_gitignore(directory):
    """
    Reads the .gitignore file in the given directory and returns a list of patterns.
    Note: This function only reads the .gitignore in the specified directory,
    it does not implement cascading behavior from parent directories like Git.

    Args:
        directory (str): The directory containing the .gitignore file.

    Returns:
        list: A list of ignore patterns, or an empty list if .gitignore is not found.
    """
    gitignore_path = os.path.join(directory, ".gitignore")
    patterns = []
    if os.path.exists(gitignore_path):
        try:
            with open(gitignore_path, 'r', encoding='utf-8') as f:
                # Filter out empty lines and lines starting with '#' (comments)
                patterns = [line.strip() for line in f if line.strip() and not line.startswith("#")]
        except Exception as e:
            print(f"Error reading .gitignore file {gitignore_path}: {e}")
    return patterns

def crawl_tsx_and_save_with_gitignore(directory, output_file="tsx_content.txt", max_depth=None):
    """
    Crawls through a directory using os.walk up to a specified depth, finds all .tsx files,
    respects .gitignore (from the starting directory), and saves their names and content
    into a text file.

    Args:
        directory (str): The path to the directory to crawl.
        output_file (str, optional): The name of the output text file.
            Defaults to "tsx_content.txt".
        max_depth (int, optional): The maximum recursion depth (0 for current directory only).
                                   If None, crawls fully.
    """
    # Ensure the starting directory exists
    if not os.path.isdir(directory):
        print(f"Error: Directory not found or is not a directory: {directory}")
        return

    # Read gitignore patterns only once from the starting directory
    ignore_patterns = read_gitignore(directory)

    try:
        with open(output_file, 'w', encoding='utf-8') as outfile:
            # Determine the depth of the starting directory to calculate relative depth
            # Using os.path.abspath to handle cases like "." or ".." correctly
            abs_start_dir = os.path.abspath(directory)
            start_depth = abs_start_dir.count(os.sep)

            # Walk the directory tree
            for root, dirs, files in os.walk(directory, followlinks=False):
                # Calculate the current depth relative to the starting directory
                # Ensure we're comparing against the absolute path of the root
                abs_root = os.path.abspath(root)
                current_depth = abs_root.count(os.sep) - start_depth

                # Apply max depth limit: if current_depth exceeds max_depth,
                # skip processing this directory and prevent further recursion from here.
                if max_depth is not None and current_depth > max_depth:
                    # Clear the 'dirs' list for the current level to prevent os.walk
                    # from visiting subdirectories within this directory.
                    dirs.clear()
                    # print(f"DEBUG: Max depth ({max_depth}) reached at {os.path.relpath(root, directory)}. Skipping files and subdirectories.") # Optional debug print
                    continue # Skip processing files in this directory as well

                # Filter directories based on gitignore *before* os.walk recurses into them
                # Iterate through the 'dirs' list backwards to safely remove items
                i = len(dirs) - 1
                while i >= 0:
                    dir_name = dirs[i]
                    dir_path = os.path.join(root, dir_name)
                    relative_dir_path = os.path.relpath(dir_path, directory)

                    if should_ignore(relative_dir_path, ignore_patterns):
                        print(f"Ignored directory (not recursing): {relative_dir_path} (matches .gitignore)")
                        del dirs[i] # Remove from list so os.walk doesn't visit it
                    i -= 1

                # Process files in the current directory 'root'
                for file_name in files:
                    # Check if the file is a .tsx file
                    if file_name.endswith(".tsx"):
                        file_path = os.path.join(root, file_name)
                        relative_file_path = os.path.relpath(file_path, directory)

                        # Check if the file should be ignored
                        if should_ignore(relative_file_path, ignore_patterns):
                            print(f"Ignored: {relative_file_path} (matches .gitignore)")
                            continue # Skip this file

                        # Process the .tsx file
                        try:
                            with open(file_path, 'r', encoding='utf-8') as infile:
                                content = infile.read()
                                outfile.write(f"Filename: {relative_file_path}\n")
                                outfile.write(f"Content:\n{content}\n")
                                outfile.write("-" * 40 + "\n")  # Separator
                            print(f"Processed: {relative_file_path}") # Keep processing print to see progress
                        except Exception as e:
                            print(f"Error reading file {file_path}: {e}")

        print(f"\nSuccessfully saved content of relevant .tsx files to: {output_file}")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TSX Context Crawler")
    # Define the required positional argument for the directory
    parser.add_argument("directory", help="The path to the directory to crawl")
    # Define optional arguments with appropriate types and defaults
    parser.add_argument("--full", action="store_true", help="Crawl the directory with full recursion (i.e., no maximum depth)")
    parser.add_argument("--output", default="tsx_content.txt", help="The name of the output text file (default: tsx_content.txt)")
    parser.add_argument("--max-depth", type=int, default=DEFAULT_RECURSION_DEPTH,
                        help=f"The maximum recursion depth (default: {DEFAULT_RECURSION_DEPTH}). Ignored if --full is used.")

    # Parse the arguments provided by the user
    args = parser.parse_args()

    # Use the parsed arguments to set the variables for the crawler function
    target_directory = args.directory
    output_file_name = args.output

    # Determine the effective max_depth: if --full is true, set depth to None, otherwise use args.max_depth
    if args.full:
        max_recursion_depth = None
        print(f"Crawling directory: {target_directory} with full recursion (--full specified).")
    else:
        # Use the value from args.max_depth (either user-provided or the default)
        max_recursion_depth = args.max_depth
        print(f"Crawling directory: {target_directory} with a maximum depth of {max_recursion_depth}.")

    print(f"Output file: {output_file_name}")

    # Call the main crawling function with the determined parameters
    crawl_tsx_and_save_with_gitignore(target_directory, output_file=output_file_name, max_depth=max_recursion_depth)