name: Bug Report
description: Let us know if something is broken on PyDM.
type: 'bug'
body:

  - type: markdown
    attributes:
      value: |
        *Before reporting:*
        - Confirm the problem is reproducible on [**master**](https://github.com/neovim/neovim/releases/nightly) or [**latest stable**](https://github.com/neovim/neovim/releases/stable) release
        - Search [existing issues](https://github.com/neovim/neovim/issues?q=is%3Aissue+is%3Aopen+label%3Abug,bug-crash) (including [closed](https://github.com/neovim/neovim/issues?q=is%3Aissue+is%3Aclosed+label%3Abug%2Cbug-crash))

  - type: textarea
    attributes:
      label: "Describe the bug"
      description: "A clear and concise description the bug. May include logs, images, or videos."
    validations:
      required: true
  - type: textarea
    attributes:
      label: "Steps to reproduce"
      description: "Steps to reproduce the bug"
    validations:
      required: true
  - type: textarea
    attributes:
      label: "Expected behavior"
      description: "A clear and concise description of what you expected to happen."
    validations:
      required: true

  - type: dropdown
    id: os-version
    attributes:
      label: "Operating System"
      description: "Select your OS version"
      options:
        - Linux
        - Windows
        - macOS
    validations:
      required: true

  - type: dropdown
    id: python-version
    attributes:
      label: "Python Version"
      description: "Select your Python version"
      options:
        - "3.6"
        - "3.7"
        - "3.8"
        - "3.9"
        - "3.10"
        - "3.11"
        - "3.12"
    validations:
      required: true

  - type: textarea
    id: package-versions
    attributes:
      label: "Packages Version"
      description: "Provide package versions (Check `File > About` in PyDM)"
      placeholder: "Example: PyDM 1.24.1, NumPy 1.23.4, PyQt 5.15.2"
    validations:
      required: true

  - type: textarea
    attributes:
      label: "Additional context."
      description: "Add any other context, links, etc. about the feature here."
    validations:
      required: true