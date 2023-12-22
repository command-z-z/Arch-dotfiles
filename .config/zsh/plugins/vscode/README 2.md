# vscode
An Oh My Zsh plugin to open files in Visual Studio Code.

### Requirements

 * [Visual Studio Code](https://code.visualstudio.com/)


### Installation

#### Manual

1. Clone this repository somewhere on your machine. This guide will assume `~/.zsh/vscode`.

  ```sh
  git clone https://github.com/valentinocossar/vscode.git ~/.zsh/vscode
  ```

2. Add the following to your `.zshrc`:

  ```sh
  source ~/.zsh/vscode/vscode.plugin.zsh
  ```

3. Start a new terminal session.

#### Oh My Zsh

1. Clone this repository into `$ZSH_CUSTOM/plugins` (by default `~/.oh-my-zsh/custom/plugins`)

  ```sh
  git clone https://github.com/valentinocossar/vscode.git $ZSH_CUSTOM/plugins/vscode
  ```

2. Add the plugin to the list of plugins for Oh My Zsh to load:

  ```sh
  plugins=(vscode)
  ```

3. Start a new terminal session.


### Usage

 * If `vs` command is called without an argument, launch Visual Studio Code.

 * If `vs` is passed a directory, `cd` to it and open it in Visual Studio Code.

 * If `vsa` is passed a directory, `cd` to it and open it in the last active Visual Studio Code window.

 * If `vs` is passed a file, open it in Visual Studio Code.

 * If `vsa` is passed a file, open it in the last active Visual Studio Code window.

 * If `vst` command is called, it is equivalent to `vs .`, opening the current folder in Visual Studio Code.

 * If `vsta` command is called, it is equivalent to `vs -a .`, opening the current folder in the last active Visual Studio Code window.

 * If `svs` command is called, it is like `sudo vs`, opening the file or folder in Visual Studio Code. Useful for editing system protected files.

 * If `svsa` command is called, it is like `sudo vs -a`, opening the file or folder in the last active Visual Studio Code window. Useful for editing system protected files.