# terraform_tutorial
A template repo for terraform and subsequent dev work

## Repo Setup
- First Installation with **poetry**
  - If there are multiple python installations present on the system run the foollowingn to allow petry to use a specific python installation (replace the xx in the following example with your favorite version, e.g. 11):
    ```bash
    #!/bin/bash
    poetry env use python3.xx
    ```
  - Then  run the following:
    ```bash
    #!/bin/bash
    poetry install
    ```
- If **pre-commit** not installed then install using ```pip install pre-commit```. Ensure to use the pip matched to the same python version you have set poetry to use above
- Run **pre-commit install** to set up the git hook scripts
