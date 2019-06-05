# pyPlexUtils

A Python package which includes useful command-line tools for managing media files for use with Plex Media Server.

## Table of Contents

  - [Getting Started](#getting-started)
    - [Prerequisites](#prerequisites)
    - [Installation](#installation)
    - [Usage](#usage)

## Getting Started

### Prerequisites

The command-line tool, `clear-mkvchptnames`, included with this pyPlexUtils Python package requires the [Matroska tools](https://mkvtoolnix.download/) to be installed on your system.  The Matroska tools includes a set of command-line tools which should be accessible from the shell PATH upon installation.

> On macOS, the Matroska tools can be installed using the [Homebrew](https://brew.sh/) package manager.  From the terminal, type `brew install mkvtoolnix` and press Enter.


### Installation

> It is recommended to perform the install using pipx.  Pipx allows you to execute binaries from Python packages in isolated environments.  This is generally good housekeeping and helps to maintain a tidy global python environment on your system.  Here's how to install pipx:
>    ```sh
>    $ python3 -m pip install pipx
>    $ python3 -m userpath append ~/.local/bin
>    ```
>The last command updates your path if your system is configured to use the bash shell.  However, if your system is configured to use zsh instead of bash, you will need to edit the ~./zshrc to include `export PATH="$PATH:/Users/<your_user_name>/.local/bin"` where <your_user_name> is your specific user name.

Here's how to install pyPlexUtils:

```sh
$ pipx install --spec git+https://git@github.com/JoeArauzo/pyPlexUtils.git pyPlexUtils
```

### Usage

Once the package is installed, the following executable is available from the shell.

```sh
CLEAR-MKVCHPTNAMES
--------------------
Usage: clear-mkvchptnames [OPTIONS] FILE

  This command-line tool inspects the metadata of a Matroska (MKV) media
  file for chapters and clears the names assigned to each chapter.  This is
  to ensure interoperability with Plex Media Server (https://www.plex.tv)
  which requires MKV chapter names to be unnamed.

  Matroska tools (https://mkvtoolnix.download/) needs to already be
  installed and accessible from the shell PATH in order for this tool to
  run.

Options:
  -v, --verbose         Verbose output
  -b, --backupchapters  Backup chapters as xml file.
  --help                Show this message and exit.
```

## Versioning

- 0.1.0 — (2019-06-04) first release

## Authors

- Joe Arauzo - https://github.com/JoeArauzo

## License

GNU GENERAL PUBLIC LICENSE
Version 3, 29 June 2007