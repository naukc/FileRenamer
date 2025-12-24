# FileRenamer

A simple, user-friendly web application for batch renaming files in a selected directory. This tool provides a web interface to define various renaming rules and preview the changes before applying them.

## Features

- **Folder Selection:** Easily select a target folder using a native file dialog (macOS) or a fallback GUI (Windows/Linux).
- **Rule-Based Renaming:** Apply multiple renaming rules including:
    - **Replace:** Find and replace text within filenames.
    - **New Name:** Set a completely new name for files (can be combined with other rules).
    - **Prepend/Append:** Add text to the beginning or end of filenames.
    - **Counter:** Insert sequential numbers into filenames with customizable start, step, padding, separator, and position.
    - **Extension:** Change file extensions.
- **Live Preview:** See a real-time preview of how files will be renamed before committing any changes.
- **Collision Detection:** Prevents renaming if it would result in duplicate filenames.
- **Cross-Platform:** Runs on macOS, Windows, and Linux.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/naukc/FileRenamer.git
    cd FileRenamer
    ```

2.  **Create and activate a virtual environment (recommended):**
    ```bash
    python -m venv venv
    # On Windows
    .\venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Install Tkinter (if not already present):**
    Tkinter is usually included with Python, but sometimes it needs to be installed separately depending on your operating system and Python distribution.

    -   **macOS:** Tkinter is typically pre-installed with Python. If you installed Python via Homebrew, you might need to ensure `python-tk` is installed.
    -   **Windows:** Tkinter is usually included with standard Python distributions.
    -   **Linux (e.g., Debian/Ubuntu):** You might need to install it via your package manager:
        ```bash
        sudo apt-get update
        sudo apt-get install python3-tk
        ```
        (Replace `python3-tk` with `python-tk` or similar for other distributions if needed).


## Usage

1.  **Start the application:**
    ```bash
    python app.py
    ```
    Your default web browser should automatically open to `http://127.0.0.1:5001/`. If not, open it manually.

2.  **Select a Folder:**
    - On the web interface, click the "Select Folder" button.
    - Choose the directory containing the files you wish to rename.

3.  **Define Renaming Rules:**
    - Use the provided interface to add and configure renaming rules. You can combine multiple rules.
    - **Example Rules:**
        - **Replace:** `old_string` with `new_string`
        - **Counter:** Start at `1`, step by `1`, pad with `3` zeros, use `_` as separator, position at `end`.
        - **Prepend:** Add `Prefix_`
        - **Extension:** Change to `txt`

4.  **Preview Changes:**
    - As you add or modify rules, the "Preview" section will update to show the original and new filenames.
    - Files that will be changed are highlighted.

5.  **Rename Files:**
    - Once you are satisfied with the preview, click the "Rename Files" button to apply the changes.
    - The application will report the number of files renamed and any errors encountered.

## Development and Testing

### Running Tests

Tests are written using `pytest`. To run them:

1.  **Activate your virtual environment (if not already active):**
    ```bash
    source venv/bin/activate # macOS/Linux
    .\venv\Scripts\activate   # Windows
    ```

2.  **Run pytest:**
    ```bash
    pytest
    ```

### Project Structure

-   `app.py`: The main Flask application, containing routes and business logic for file renaming.
-   `requirements.txt`: Lists all Python dependencies.
-   `static/`: Contains static assets like `script.js` (frontend logic) and `style.css` (styling).
-   `templates/`: Contains HTML templates, primarily `index.html`.
-   `test_renamer.py`: Unit and integration tests for the renaming logic.
-   `build/`, `dist/`: Build artifacts (e.g., from PyInstaller).

## Contributing

Feel free to fork the repository, make improvements, and submit pull requests.

## License

This project is open-source and available under the [MIT License](LICENSE).
