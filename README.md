**TSX Context Crawler**
================================

**Overview**
------------

This script is a simple TSX crawler designed to provide context for a chatbot. It recursively crawls through a specified directory, finds all `.tsx` files, respects `.gitignore` patterns (from the starting directory), and saves their names and content into a text file.

**Usage**
-----

To use this script, simply run it from the command line, providing the target directory as a required argument. You can also specify optional arguments for the output file name and maximum recursion depth.

```bash
python crawler.py <directory> [options]
```

**Command Line Arguments**
-------------------------

* **Positional Argument:**
    * `directory`: **(Required)** The path to the directory to crawl.

* **Optional Arguments:**
    * `-h`, `--help`: Display the help message and exit.
    * `--full`: Crawl the directory with full recursion (i.e., no maximum depth). Overrides `--max-depth` if both are used.
    * `--output <output_file>`: The name of the output text file (default: `tsx_content.txt`).
    * `--max-depth <max_depth>`: The maximum recursion depth (default: `3`). Depth 0 is the starting directory itself.

**Example Usage**
----------------

1.  **Basic usage (crawl current directory with default depth and output):**
    ```bash
    python crawler.py .
    ```
    This crawls the current directory (`.`) with a maximum recursion depth of 3 and saves to `tsx_content.txt`.

2.  **Crawl a specific directory with default options:**
    ```bash
    python crawler.py /path/to/your/project
    ```
    This crawls `/path/to/your/project` with a maximum recursion depth of 3 and saves to `tsx_content.txt`.

3.  **Crawl with a specific maximum depth:**
    ```bash
    python crawler.py /path/to/your/project --max-depth 5
    ```
    This crawls `/path/to/your/project` with a maximum recursion depth of 5 and saves to `tsx_content.txt`.

4.  **Crawl with a specific output file name:**
    ```bash
    python crawler.py /path/to/your/project --output my_tsx_content.log
    ```
    This crawls `/path/to/your/project` with a maximum recursion depth of 3 and saves to `my_tsx_content.log`.

5.  **Crawl with a specific depth and output file:**
    ```bash
    python crawler.py /path/to/your/project --max-depth 10 --output all_tsx.txt
    ```
    This crawls `/path/to/your/project` with a maximum recursion depth of 10 and saves to `all_tsx.txt`.

6.  **Perform a full recursive crawl (no depth limit):**
    ```bash
    python crawler.py /path/to/your/project --full
    ```
    This crawls `/path/to/your/project` through all subdirectories and saves to `tsx_content.txt`.

7.  **Perform a full recursive crawl with a specific output file:**
    ```bash
    python crawler.py /path/to/your/project --full --output full_crawl.txt
    ```
    This crawls `/path/to/your/project` fully and saves to `full_crawl.txt`.

**How it Works**
----------------

1.  The script reads the `.gitignore` file in the target directory and extracts ignore patterns.
2.  It uses `os.walk` to traverse the directory tree, respecting the specified maximum depth and skipping directories and files that match the ignore patterns.
3.  If a file encountered during traversal is a `.tsx` file and does not match any ignore patterns, its content is read and saved to the output file.
4.  The script continues until all relevant files within the specified depth have been processed.

**Functions**
-------------

* `read_gitignore(directory)`: Reads the `.gitignore` file in the given directory and returns a list of patterns found at that top level.
* `should_ignore(path, ignore_patterns)`: Checks if a given relative path (file or directory) should be ignored based on the provided list of patterns.
* `crawl_tsx_and_save_with_gitignore(directory, output_file, max_depth)`: The main function that orchestrates the directory traversal, filtering, and file processing.

**Notes**
-------

* The script reads `.gitignore` patterns only from the **initial target directory**, not from `.gitignore` files in subdirectories.
* The script uses the `fnmatch` module to match file paths against ignore patterns.
* The script uses `os.walk` for directory traversal, which is more robust against issues like symbolic link loops compared to manual recursion.