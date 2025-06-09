# Developer's Guide

1. Start by forking the main repository: [https://github.com/weecology/MillionAnimals](https://github.com/weecology/MillionAnimals).
2. Clone your fork of the repository:

    - Using HTTPS: `git clone https://github.com/myUserName/MillionAnimals.git`
    - Using SSH: `git clone git@github.com:myUserName/MillionAnimals.git`

3. Link your cloned repository to the main repository (typically named `upstream`):

    - `git remote add upstream https://github.com/weecology/MillionAnimals.git`

5. Verify your remote settings with:

    ```bash
    git remote -v
    ```

    You should see output similar to:

    ```
    origin    git@github.com:myUserName/MillionAnimals.git (fetch)
    origin    git@github.com:myUserName/MillionAnimals.git (push)
    upstream  https://github.com/weecology/MillionAnimals.git (fetch)
    upstream  https://github.com/weecology/MillionAnimals.git (push)
    ```

6. Install the package from the main directory. Use the `-U` or `--upgrade` flag to update or overwrite any previously installed versions:

    ```bash
    pip install . -U
    ```

## Running Tests Locally

[Add specific instructions for running tests if necessary.]

## Create Release

[Add specific instructions for creating a release if necessary.]

## Documentation

We use [Sphinx](http://www.sphinx-doc.org/en/stable/) and [Read the Docs](https://readthedocs.org/) for our documentation. Sphinx supports both reStructuredText and markdown as markup languages. 

Source code documentation is automatically included after committing to the main repository. To add additional supporting documentation, create new reStructuredText or markdown files in the `docs` folder.

If you need to reorganize the documentation, refer to the [Sphinx documentation](http://www.sphinx-doc.org/en/stable/).

### Update Documentation

The documentation is automatically updated for changes within modules. **However, it is essential to update the documentation after adding new modules** in the `engines` or `lib` directories.

1. Navigate to the `docs` directory and create a temporary directory, e.g., `source`.
2. Run the following command to generate documentation:

    ```bash
    cd docs
    mkdir source
    sphinx-apidoc -f -o ./source /Users/..../MillionAnimals/millionanimals/
    ```

   In this example, `source` is the destination folder for the generated `.rst` files, and `/Users/..../MillionAnimals/millionanimals/` is the path to the `millionanimals` source code.

3. Review the generated files, make necessary edits to ensure accuracy, and then commit and push the changes.

### Test Documentation Locally

To test the documentation locally:

    ```bash
    cd docs  # Navigate to the docs directory
    make html && python3 -m http.server --directory _build/html
    ```

   This command generates the HTML files and hosts a local HTTP server on `localhost:8000`, allowing you to view the documentation in your browser.

> **Note:** Do not commit the `_build` directory after generating HTML.