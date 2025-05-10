import re
import os

def create_inline_html_from_files(base_directory="campaign-manager", output_filename="campaign-tracker.html"):
    """
    Reads an index.html file, inlines its local JavaScript files,
    and saves the result to a new HTML file.

    Args:
        base_directory (str): The root directory of the campaign manager project
                              (e.g., "campaign-manager"). This directory should
                              contain index.html and the js/trackers subdirectories.
        output_filename (str): The name of the output HTML file to be created
                               (e.g., "campaign-tracker.html"). This file will be
                               created in the same base_directory.
    """
    index_html_path = os.path.join(base_directory, "index.html")
    output_html_path = os.path.join(base_directory, output_filename)

    try:
        with open(index_html_path, "r", encoding="utf-8") as f:
            html_content = f.read()
        print(f"Successfully read '{index_html_path}'.")
    except FileNotFoundError:
        print(f"Error: Input file '{index_html_path}' not found. "
              f"Please ensure the script is run from a directory that can access '{base_directory}' "
              f"or adjust the base_directory path.")
        return
    except Exception as e:
        print(f"Error reading '{index_html_path}': {e}")
        return

    # Regex to find local script tags: <script src="path/to/file.js"></script>
    # It avoids matching tags with http/https in src (for CDNs).
    script_tag_pattern = re.compile(r'<script\s+src="(?!(?:http|https):)([^"]+\.js)"></script>')

    def replace_script_tag_with_content(match):
        js_relative_path = match.group(1)  # e.g., "js/main.js" or "js/trackers/someTracker.js"
        
        # Construct the full path to the JS file, relative to the base_directory
        js_full_path = os.path.join(base_directory, js_relative_path)
        
        try:
            with open(js_full_path, "r", encoding="utf-8") as js_file:
                js_content = js_file.read()
            # Add a comment indicating the source of the inlined script for clarity
            print(f"  Inlining content from '{js_full_path}'...")
            return f'<script>\n\n{js_content}\n</script>'
        except FileNotFoundError:
            print(f"  Warning: JS file not found at '{js_full_path}'. "
                  f"Keeping original tag for '{js_relative_path}'.")
            return match.group(0)  # Return the original script tag if the JS file is not found
        except Exception as e:
            print(f"  Warning: Error reading JS file '{js_full_path}': {e}. "
                  f"Keeping original tag for '{js_relative_path}'.")
            return match.group(0)

    print("Starting JavaScript inlining process...")
    modified_html_content = script_tag_pattern.sub(replace_script_tag_with_content, html_content)

    try:
        with open(output_html_path, "w", encoding="utf-8") as f:
            f.write(modified_html_content)
        print(f"Successfully created '{output_html_path}' with inlined JavaScript.")
    except IOError as e:
        print(f"Error writing to output file '{output_html_path}': {e}")
    except Exception as e:
        print(f"An unexpected error occurred during file writing: {e}")

if __name__ == "__main__":
    # This assumes your Python script is in the directory that *contains*
    # the 'campaign-manager' folder.
    # For example, if your structure is:
    # /my_project/
    #   |- inliner.py  <-- (this script)
    #   |- campaign-manager/
    #      |- index.html
    #      |- js/
    #      |- css/
    #
    # If your script is *inside* the 'campaign-manager' folder, you would call:
    create_inline_html_from_files(base_directory=".", output_filename="campaign-tracker.html")

    # create_inline_html_from_files(base_directory="campaign-manager", output_filename="campaign-tracker.html")