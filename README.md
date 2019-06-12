# Jackin4Beats

A Python package which includes CLI tools useful for processing audio files.

## Table of Contents

  - [Getting Started](#getting-started)
    - [Prerequisites](#prerequisites)
    - [Installation](#installation)
    - [Usage](#usage)
  - [Versioning](#versioning)
  - [Authors](#authors)
  - [License](#license)

## Getting Started

### Prerequisites

The command-line tool, `trim-audiosilence`, included with this Python package has the following dependencies.

#### Kid3 Tag Editor
[Kid3 Tag Editor](https://sourceforge.net/projects/kid3/) needs to be installed on your system.  The Kid3 Tag Editor includes `kid3-cli` which should be accessible from the shell PATH upon installation.
> On macOS, the Kid3 Tag Editor can be installed using the [Homebrew](https://brew.sh/) package manager.  From the terminal, type `brew cask install kid3` and press Enter.

#### FFmpeg
[FFmpeg](https://ffmpeg.org/) needs to be installed on your system.  `ffmpeg` should be accessible from the shell PATH upon installation.
> On macOS, FFmpeg can be installed using the [Homebrew](https://brew.sh/) package manager.  From the terminal, type `brew install ffmpeg` and press Enter.

#### TagLib
[TagLib](https://taglib.org/) needs to be installed on your system.
> On macOS, TagLib can be installed using the [Homebrew](https://brew.sh/) package manager.  From the terminal, type `brew install taglib` and press Enter.


### Installation

> It is recommended to perform the install using pipx.  Pipx allows you to execute binaries from Python packages in isolated environments.  This is generally good housekeeping and helps to maintain a tidy global python environment on your system.  Here's how to install pipx:
>    ```sh
>    $ python3 -m pip install pipx
>    $ python3 -m userpath append ~/.local/bin
>    ```
>The last command updates your path if your system is configured to use the bash shell.  However, if your system is configured to use zsh instead of bash, you will need to edit the ~./zshrc to include `export PATH="$PATH:/Users/<your_user_name>/.local/bin"` where <your_user_name> is your specific user name.

Here's how to install Jackin4Beats:

```sh
$ pipx install --spec git+https://github.com/JoeArauzo/Jackin4Beats.git Jackin4Beats
```

### Usage

Once the package is installed, the following executable is available from the shell.

```sh
TRIM-AUDIOSILENCE
--------------------
Usage: trim-audiosilence [OPTIONS] FILE

  This command-line tool removes leading and trailing silence from an AIFF
  audio file.

Options:
  -t, --threshold <dB>     threshold (default: -96.0 dB)
  -b, --begin_offset <ms>  beggining offset (default: 0 ms)
  -e, --end_offset <ms>    ending offset (default: 0 ms)
  --namefromtag            Name trimmed file '{artist} - {title}'
  --test                   Perform test run without making changes
  --verbose                Verbose output
  --debug                  Debug output
  --help                   Show this message and exit.
```

## Versioning

- 0.1.0 — (2019-06-?) first release

## Authors

- Joe Arauzo - https://github.com/JoeArauzo

## License

GNU GENERAL PUBLIC LICENSE
Version 3, 29 June 2007