#...

# Automation for setting up my os
* [manifest.yml](./manifest.yml) is the main spec file
* [manifest.py](./manifest.py) is the script that drives it

# Symlink file under root/
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
