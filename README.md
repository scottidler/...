#... an automation repo that sits in $HOME right next to . and ..

# Automation for setting up my os
* [manifest.yml](./manifest.yml) is the main spec file
* [manifest.py](./manifest.py) is the script that drives it

## manifest.py --help
```
$> ./manifest.py --help
usage: manifest.py [-h] [-C CONFIG] [-D CWD] [-U USER] [-M PKGMGR]
                   [-l [LINK [LINK ...]]] [-p [PPA [PPA ...]]]
                   [-a [APT [APT ...]]] [-d [DNF [DNF ...]]]
                   [-n [NPM [NPM ...]]] [-P [PIP3 [PIP3 ...]]]
                   [-X [PIPX [PIPX ...]]] [-g [GITHUB [GITHUB ...]]]
                   [-s [SCRIPT [SCRIPT ...]]]

optional arguments:
  -h, --help            show this help message and exit
  -C CONFIG, --config CONFIG
                        default="/home/sidler/.../manifest.yml"; specify the
                        config path
  -D CWD, --cwd CWD     default="/home/sidler/..."; set the cwd
  -U USER, --user USER  default="sidler"; specify user if not current
  -M PKGMGR, --pkgmgr PKGMGR
                        default="deb"; override pkgmgr
  -l [LINK [LINK ...]], --link [LINK [LINK ...]]
                        specify list of glob patterns to match links
  -p [PPA [PPA ...]], --ppa [PPA [PPA ...]]
                        specify list of glob patterns to match ppa items
  -a [APT [APT ...]], --apt [APT [APT ...]]
                        specify list of glob patterns to match apt items
  -d [DNF [DNF ...]], --dnf [DNF [DNF ...]]
                        specify list of glob patterns to match dnf items
  -n [NPM [NPM ...]], --npm [NPM [NPM ...]]
                        specify list of glob patterns to match npm items
  -P [PIP3 [PIP3 ...]], --pip3 [PIP3 [PIP3 ...]]
                        specify list of glob patterns to match pip3 items
  -X [PIPX [PIPX ...]], --pipx [PIPX [PIPX ...]]
                        specify list of glob patterns to match pipx items
  -g [GITHUB [GITHUB ...]], --github [GITHUB [GITHUB ...]]
                        specify list of glob patterns to match github repos
  -s [SCRIPT [SCRIPT ...]], --script [SCRIPT [SCRIPT ...]]
                        specify list of glob patterns to match script names

```

The manifest.py script will only print out valid bash to perform the install.  It is then up to the user to pipe to bash to get it to execute.  In this way you can see what will be done before executing it.

### example 1
```
$> ./manifest.py --link
#!/bin/bash
# generated file by manifest.py
# src: https://github.com/scottidler/.../blob/master/manifest.py

if [ -n "$DEBUG" ]; then
    PS4=':${LINENO}+'
    set -x
fi

linker() {
    file=$(realpath "$1")
    link="${2/#\~/$HOME}"
    echo "$link -> $file"
    if [ -f "$link" ] && [ "$file" != "$(readlink $link)" ]; then
        orig="$link.orig"
        $VERBOSE && echo "backing up $orig"
        mv $link $orig
    elif [ ! -f "$link" ] && [ -L "$link" ]; then
        $VERBOSE && echo "removing broken link $link"
        unlink $link
    fi
    if [ -f "$link" ]; then
        echo "[exists] $link"
    else
        echo "[create] $link -> $file"
        mkdir -p $(dirname $link); ln -s $file $link
    fi
}

echo "links:"
while read -r file link; do
    linker $file $link
done<<EOM
/home/sidler/.../root/home/USER/.gitconfig /home/sidler/.gitconfig
/home/sidler/.../root/home/USER/.shell-exports /home/sidler/.shell-exports
/home/sidler/.../root/home/USER/.expand-alias /home/sidler/.expand-alias
/home/sidler/.../root/home/USER/.vimrc /home/sidler/.vimrc
/home/sidler/.../root/home/USER/.bashrc /home/sidler/.bashrc
/home/sidler/.../root/home/USER/.zshrc /home/sidler/.zshrc
/home/sidler/.../root/home/USER/.git-prompt.sh /home/sidler/.git-prompt.sh
/home/sidler/.../root/home/USER/.shell-aliases /home/sidler/.shell-aliases
/home/sidler/.../root/home/USER/.ssh-ident /home/sidler/.ssh-ident
/home/sidler/.../root/home/USER/.zsh-dircolors.config /home/sidler/.zsh-dircolors.config
/home/sidler/.../root/home/USER/.shell-functions /home/sidler/.shell-functions
/home/sidler/.../root/home/USER/.tmux.conf /home/sidler/.tmux.conf
/home/sidler/.../root/home/USER/.bash_prompt /home/sidler/.bash_prompt
/home/sidler/.../root/home/USER/.gnupg/gpg.conf /home/sidler/.gnupg/gpg.conf
/home/sidler/.../root/home/USER/.ssh/config /home/sidler/.ssh/config
/home/sidler/.../root/home/USER/.vim/syntax/ragel.vim /home/sidler/.vim/syntax/ragel.vim
/home/sidler/.../root/home/USER/.config/autostart/touchpad.desktop /home/sidler/.config/autostart/touchpad.desktop
/home/sidler/.../root/home/USER/.config/rmrf/rmrf.cfg /home/sidler/.config/rmrf/rmrf.cfg
/home/sidler/.../root/home/USER/.config/pip/pip.conf /home/sidler/.config/pip/pip.conf
/home/sidler/.../root/home/USER/.config/tmp/tmp.yml /home/sidler/.config/tmp/tmp.yml
/home/sidler/.../root/home/USER/.config/layout/mint-3840x2160.yml /home/sidler/.config/layout/mint-3840x2160.yml
/home/sidler/.../root/home/USER/.config/clone/clone.cfg /home/sidler/.config/clone/clone.cfg
/home/sidler/.../root/home/USER/.config/pianobar/config /home/sidler/.config/pianobar/config
/home/sidler/.../root/home/USER/bin/manifest /home/sidler/bin/manifest
EOM

```
### example 2
Any option like `--apt` below, can be given patterns to match against. In this case `lib` matches against several packages.
```
$> ./manifest.py --apt lib
#!/bin/bash
# generated file by manifest.py
# src: https://github.com/scottidler/.../blob/master/manifest.py

if [ -n "$DEBUG" ]; then
    PS4=':${LINENO}+'
    set -x
fi

echo "apts:"

sudo apt update && sudo apt upgrade -y && sudo apt install -y software-properties-common

sudo apt install -y libsmbclient-dev \
    libffi-dev \
    libicu-dev \
    libssl-dev \
    libffi-dev \
    libcurl4-openssl-dev \
    librsync-dev \
    libglib2.0-dev \
    libgirepository1.0-dev \
    libcairo2-dev \
    libjpeg-dev \
    libgif-dev \
    libxml2-dev \
    libxmlsec1-dev \
    libcups2-dev \
    libkrb5-dev

```

### example 3
In this case `oh-my-zhs` matches against `robbyrussel/oh-my-zsh`.
```
$> ./manifest.py --github oh-my-zsh
#!/bin/bash
# generated file by manifest.py
# src: https://github.com/scottidler/.../blob/master/manifest.py

if [ -n "$DEBUG" ]; then
    PS4=':${LINENO}+'
    set -x
fi

linker() {
    file=$(realpath "$1")
    link="${2/#\~/$HOME}"
    echo "$link -> $file"
    if [ -f "$link" ] && [ "$file" != "$(readlink $link)" ]; then
        orig="$link.orig"
        $VERBOSE && echo "backing up $orig"
        mv $link $orig
    elif [ ! -f "$link" ] && [ -L "$link" ]; then
        $VERBOSE && echo "removing broken link $link"
        unlink $link
    fi
    if [ -f "$link" ]; then
        echo "[exists] $link"
    else
        echo "[create] $link -> $file"
        mkdir -p $(dirname $link); ln -s $file $link
    fi
}

echo "github repos:"

echo "robbyrussell/oh-my-zsh:"
git clone --recursive https://github.com/robbyrussell/oh-my-zsh /home/sidler/.../repos/robbyrussell/oh-my-zsh
(cd /home/sidler/.../repos/robbyrussell/oh-my-zsh && pwd && git pull && git checkout HEAD)
echo "links:"
while read -r file link; do
    linker $file $link
done<<EOM
/home/sidler/.../repos/robbyrussell/oh-my-zsh/./ ~/.oh-my-zsh
EOM
```

## `link` section in manifest.yml
The link section specifies mapping root in the git repo to / on the system. Recursive is self-explanatory.

### Symlink files under root/
Note: USER will be substituted for the value of $USER
```
root
└── home
    └── USER
        ├── .bash_prompt
        ├── .bashrc
        ├── bin
        │   └── manifest -> ../../../../manifest.py
        ├── .config
        │   ├── autostart
        │   │   └── touchpad.desktop
        │   ├── clone
        │   │   └── clone.cfg
        │   ├── layout
        │   │   └── mint-3840x2160.yml
        │   ├── pianobar
        │   │   └── config
        │   ├── pip
        │   │   └── pip.conf
        │   ├── rmrf
        │   │   └── rmrf.cfg
        │   └── tmp
        │       └── tmp.yml
        ├── .expand-alias
        ├── .gitconfig
        ├── .git-prompt.sh
        ├── .gnupg
        │   └── gpg.conf
        ├── .shell-aliases
        ├── .shell-exports
        ├── .shell-functions
        ├── .ssh
        │   └── config
        ├── .ssh-ident
        ├── .tmux.conf
        ├── .vim
        │   └── syntax
        │       └── ragel.vim
        ├── .vimrc
        ├── .zsh-dircolors.config
        └── .zshrc
```
## `ppa` section in manifest.yml
The items listed here are ppa to install on Debian systems.

## `pkg` section in manifest.yml
The items listed here are the package names that are valid for DNF and APT.

## `apt` section in manifest.yml
The items listed here are the list of package names valid for APT.

## `dnf` section in manifest.yml
The items listed here are the list of package names valid for DNF.

## `pip3` section in manifest.yml
The items to be installed via pip3.

## `pipx` section in manifest.yml
The items to be installed via pipx.

## `npm` section in manifest.yml
The items to be installed via npm.

## `github` section in manifest.yml
These github repositories are cloned | checked out to .../repos/.  The link section below is symlinks to create from path in repo to system.

## `script` section in manifest.yml
These are items that require installation steps, often copied from the download page of the software.

