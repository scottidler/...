alias dots="cd ~/..."
alias udpate="update"
alias linode="ssh root@45.33.26.141"
alias fog="ssh -A saidler@45.33.26.141"
alias cl="clear"
alias pb="pianobar"

alias ipy="sudo ipython"
alias ipy3="sudo ipython3"

alias d="docker"
alias dc="docker-compose"
alias di="docker images"
alias dps="docker ps"
alias dpsa="docker ps -a"
alias dpsaq="docker ps -aq"
alias drm="docker rm"
alias drmi="docker rmi"

alias g="git"
alias ga="git add"
alias gb="git branch"
alias gc="git commit"
alias gd="git diff"
alias gp="git pull --rebase"
alias gP="git push"
alias gs="git status --short"
alias gbc="git branch --contains"
alias gco="git checkout"
alias gcm="git checkout master"
alias grp="git rev-parse"
alias gsh="git show"
alias gsn="git show --notes=*"
alias gpo="git push origin"
alias gpP="gp && gP"
alias grh="git reset --hard"
alias grhh="git reset --hard HEAD"
alias grph="git rev-parse HEAD"
alias gfbn="git fetch origin +refs/notes/buildno/:refs/notes/buildno"
alias gfofu="git fetch origin -f -u +refs/heads/*:refs/heads/*"
alias tags="git tag -l"
alias gl="git log"

alias gbp="git-big-picture"

alias gsm="git submodule"
alias gsmu="gsm update"
alias gsmui="gsm update --jobs=$((3 * $(nproc))) --init --recursive"

alias vibashrc="vi ~/.bashrc"
alias srcbashrc=". ~/.bashrc"

alias ureboot="update && reboot"
alias ushutdown="update && shutdown"

alias grn="grep -rn"
alias pgrn="| grn"
alias egrn="egrep -rn"
alias pegrn="| egrn"
alias psgrep="ps aux | grep -v grep | grep"

alias moz="ssh moz.lan"
alias xps="ssh xps.lan"
alias pffw="ssh pffw.lan"
alias twin="ssh twin.lan"
alias fedev="ssh fedev.lan"

alias clipboard="xclip -sel clip"
alias cb="clipboard"

alias irc="irccloud-search"
alias ac="autocert"

# enable color support of ls and also add handy aliases
if [ -x /usr/bin/dircolors ]; then
    test -r ~/.dircolors && eval "$(dircolors -b ~/.dircolors)" || eval "$(dircolors -b)"
    alias ls='ls --color=auto'
    #alias dir='dir --color=auto'
    #alias vdir='vdir --color=auto'

    alias grep='grep --color=auto'
    alias fgrep='fgrep --color=auto'
    alias egrep='egrep --color=auto'
fi

# colored GCC warnings and errors
#export GCC_COLORS='error=01;31:warning=01;35:note=01;36:caret=01;32:locus=01:quote=01'

# some more ls aliases
alias lah='ls -lah --color=auto'
alias ltr='ls -ltr --color=auto'
alias ll='ls -alF --color=auto'
alias la='ls -A --color=auto'
alias l='ls -CF --color=auto'

