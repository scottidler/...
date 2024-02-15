# If you come from bash you might have to change your $PATH.

# Path to your oh-my-zsh installation.
export ZSH=$HOME/.oh-my-zsh

# ensure that the path is unique
typeset -U path

path=("$HOME/bin" $path)

# export PYENV_DEBUG=1

# macos specific nonsense
autoload -Uz compinit && compinit

# macos specific alias
gdircolors &>/dev/null && alias dircolors='gdircolors'

# Set name of the theme to load. Optionally, if you set this to "random"
# it'll load a random theme each time that oh-my-zsh is loaded.
# See https://github.com/robbyrussell/oh-my-zsh/wiki/Themes
ZSH_THEME="agnoster"

. ~/.zsh/zsh-dircolors-solarized/zsh-dircolors-solarized.zsh

HIST_SPACING_STYLE="always"

function preexec() {
  if [[ -n "$1" ]]; then
    last_command="$1"
  fi
}
function precmd() {
  if [[ -n "$last_command" ]]; then
    fc -R <(echo "$last_command ")
  fi
}

# Uncomment the following line to use case-sensitive completion.
# CASE_SENSITIVE="true"

# Uncomment the following line to use hyphen-insensitive completion. Case
# sensitive completion must be off. _ and - will be interchangeable.
# HYPHEN_INSENSITIVE="true"

# Uncomment the following line to disable bi-weekly auto-update checks.
# DISABLE_AUTO_UPDATE="true"

# Uncomment the following line to change how often to auto-update (in days).
# export UPDATE_ZSH_DAYS=13

# Uncomment the following line to disable colors in ls.
# DISABLE_LS_COLORS="true"

# Uncomment the following line to disable auto-setting terminal title.
# DISABLE_AUTO_TITLE="true"

# Uncomment the following line to enable command auto-correction.
# ENABLE_CORRECTION="true"

# Uncomment the following line to display red dots whilst waiting for completion.
# COMPLETION_WAITING_DOTS="true"

# Uncomment the following line if you want to disable marking untracked files
# under VCS as dirty. This makes repository status check for large repositories
# much, much faster.
# DISABLE_UNTRACKED_FILES_DIRTY="true"

# Uncomment the following line if you want to change the command execution time
# stamp shown in the history command output.
# The optional three formats: "mm/dd/yyyy"|"dd.mm.yyyy"|"yyyy-mm-dd"
# HIST_STAMPS="mm/dd/yyyy"

# Would you like to use another custom folder than $ZSH/custom?
# ZSH_CUSTOM=/path/to/new-custom-folder

# Which plugins would you like to load? (plugins can be found in ~/.oh-my-zsh/plugins/*)
# Custom plugins may be added to ~/.oh-my-zsh/custom/plugins/
# Example format: plugins=(rails git textmate ruby lighthouse)
# Add wisely, as too many plugins slow down shell startup.
plugins=(git)

. $ZSH/oh-my-zsh.sh

# User configuration

# export MANPATH="/usr/local/man:$MANPATH"

# You may need to manually set your language environment
# export LANG=en_US.UTF-8

# Preferred editor for local and remote sessions
# if [[ -n $SSH_CONNECTION ]]; then
#   export EDITOR='vim'
# else
#   export EDITOR='mvim'
# fi

# Compilation flags
# export ARCHFLAGS="-arch x86_64"

# ssh
# export SSH_KEY_PATH="~/.ssh/rsa_id"

# Set personal aliases, overriding those provided by oh-my-zsh libs,
# plugins, and themes. Aliases can be placed here, though oh-my-zsh
# users are encouraged to define aliases within the ZSH_CUSTOM folder.
# For a full list of active aliases, run `alias`.
#
# Example aliases
# alias zshconfig="mate ~/.zshrc"
# alias ohmyzsh="mate ~/.oh-my-zsh"

setopt clobber
unsetopt nomatch

# The next line updates PATH for the Google Cloud SDK.
if [ -f ~/src/google-cloud-sdk/path.zsh.inc ]; then
    . ~/src/google-cloud-sdk/path.zsh.inc
fi

# The next line enables shell command completion for gcloud.
if [ -f ~/src/google-cloud-sdk/completion.zsh.inc ]; then
    . ~/src/google-cloud-sdk/completion.zsh.inc
fi

if [ -d /usr/local/go/bin ]; then
    # export PATH=$PATH:/usr/local/go/bin
    path+=(/usr/local/go/bin)
fi

if hash kubectl 2> /dev/null; then
    . <(kubectl completion zsh)
fi

if [ -f ~/.acme.sh/acme.sh.env ]; then
    . ~/.acme.sh/acme.sh.env
fi

if [ -f ~/.shell-aliases ]; then
    . ~/.shell-aliases
fi

if [ -f ~/.shell-functions ]; then
    . ~/.shell-functions
fi

if [ -f ~/.shell-exports ]; then
    . ~/.shell-exports
fi

if hash aka 2>/dev/null && [ -f ~/.expand-aka ]; then
    export EXPAND_AKA=yes
    . ~/.expand-aka
fi

PROMPT_EOL_MARK=''

# remove the pipe from this zsh behavior
# https://superuser.com/questions/613685/how-stop-zsh-from-eating-space-before-pipe-symbol
ZLE_REMOVE_SUFFIX_CHARS=$' \t\n;&'

# added by travis gem
if [ -f ~/.travis/travis.sh ]; then
    . ~/.travis/travis.sh
fi

# tab complete for pyenv
# https://github.com/pyenv/pyenv#installation
# chat-gippity says this is an update
if command -v pyenv 1>/dev/null 2>&1; then
  export PYENV_ROOT="$HOME/.pyenv"
  [[ -d $PYENV_ROOT/bin ]] && path+=($PYENV_ROOT/bin)
  eval "$(pyenv init -)"
fi


if hash starship 2>/dev/null; then
    eval "$(starship init zsh)"
fi

if hash rtx 2>/dev/null; then
    eval "$(~/bin/rtx activate zsh)"
fi

# Initialize keychain for SSH keys with reduced output
# NOTE: it is important for the work to come before the home
eval $(keychain --eval --agents ssh --quiet \
    identities/work/id_ed25519 \
    identities/home/id_ed25519)

eval "$(zoxide init --cmd cd zsh)"
