alias udpate="update"

alias linode="ssh root@45.33.26.141"
alias fog="ssh -A saidler@45.33.26.141"

alias cl="clear"

alias cdp=". ~/bin/.cdp"
alias cdr=". ~/bin/.cdr"
alias cdrr=". ~/bin/.cdrr"

alias pb="pianobar"

alias ipy="ipython"
alias ipy3="ipython3"

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

function int2ip() {
    ifconfig ${1:-wlp2s0} | grep 'inet addr' | sed -e 's/:/ /' | awk '{print $3}'
}

#  Customize BASH PS1 prompt to show current GIT repository and branch.
#  by Mike Stewart - http://MediaDoneRight.com

#  SETUP CONSTANTS
#  Bunch-o-predefined colors.  Makes reading code easier than escape sequences.
#  I don't remember where I found this.  o_O

# Reset
Reset="\[\033[0m\]"           # Text Reset

# Regular Colors
Black="\[\033[0;30m\]"        # Black
Red="\[\033[0;31m\]"          # Red
Green="\[\033[0;32m\]"        # Green
Yellow="\[\033[0;33m\]"       # Yellow
Blue="\[\033[0;34m\]"         # Blue
Purple="\[\033[0;35m\]"       # Purple
Cyan="\[\033[0;36m\]"         # Cyan
White="\[\033[0;37m\]"        # White

# Bold
BBlack="\[\033[1;30m\]"       # Black
BRed="\[\033[1;31m\]"         # Red
BGreen="\[\033[1;32m\]"       # Green
BYellow="\[\033[1;33m\]"      # Yellow
BBlue="\[\033[1;34m\]"        # Blue
BPurple="\[\033[1;35m\]"      # Purple
BCyan="\[\033[1;36m\]"        # Cyan
BWhite="\[\033[1;37m\]"       # White

# Underline
UBlack="\[\033[4;30m\]"       # Black
URed="\[\033[4;31m\]"         # Red
UGreen="\[\033[4;32m\]"       # Green
UYellow="\[\033[4;33m\]"      # Yellow
UBlue="\[\033[4;34m\]"        # Blue
UPurple="\[\033[4;35m\]"      # Purple
UCyan="\[\033[4;36m\]"        # Cyan
UWhite="\[\033[4;37m\]"       # White

# Background
On_Black="\[\033[40m\]"       # Black
On_Red="\[\033[41m\]"         # Red
On_Green="\[\033[42m\]"       # Green
On_Yellow="\[\033[43m\]"      # Yellow
On_Blue="\[\033[44m\]"        # Blue
On_Purple="\[\033[45m\]"      # Purple
On_Cyan="\[\033[46m\]"        # Cyan
On_White="\[\033[47m\]"       # White

# High Intensty
IBlack="\[\033[0;90m\]"       # Black
IRed="\[\033[0;91m\]"         # Red
IGreen="\[\033[0;92m\]"       # Green
IYellow="\[\033[0;93m\]"      # Yellow
IBlue="\[\033[0;94m\]"        # Blue
IPurple="\[\033[0;95m\]"      # Purple
ICyan="\[\033[0;96m\]"        # Cyan
IWhite="\[\033[0;97m\]"       # White

# Bold High Intensty
BIBlack="\[\033[1;90m\]"      # Black
BIRed="\[\033[1;91m\]"        # Red
BIGreen="\[\033[1;92m\]"      # Green
BIYellow="\[\033[1;93m\]"     # Yellow
BIBlue="\[\033[1;94m\]"       # Blue
BIPurple="\[\033[1;95m\]"     # Purple
BICyan="\[\033[1;96m\]"       # Cyan
BIWhite="\[\033[1;97m\]"      # White

# High Intensty backgrounds
On_IBlack="\[\033[0;100m\]"   # Black
On_IRed="\[\033[0;101m\]"     # Red
On_IGreen="\[\033[0;102m\]"   # Green
On_IYellow="\[\033[0;103m\]"  # Yellow
On_IBlue="\[\033[0;104m\]"    # Blue
On_IPurple="\[\033[10;95m\]"  # Purple
On_ICyan="\[\033[0;106m\]"    # Cyan
On_IWhite="\[\033[0;107m\]"   # White

# Various variables you might want for your PS1 prompt instead
Hostname="\h"
Time12h="\T"
Time12a="\@"
PathShort="\w"
PathFull="\W"
NewLine="\n"
Jobs="\j"

function __prompt_command() {
    local EC="$?"
    PS1=""
    local Alive="º"
    local Dead="ˣ"
    local Flesh="\n><(("
    local Bones="\n>---"
    local Body=$Flesh
    local Color=$BIPurple
    local Eye=$Alive
    if [ $EC != 0 ]; then
        Eye=$Dead
    fi
    if [ -f /.docker* ]; then
        Body=$Bones
        Color=$BIGreen
    fi
    local Head="($Color$Eye$Reset>"
    local Prompt=$Body$Head
    # This PS1 snippet was adopted from code for MAC/BSD I saw from: http://allancraig.net/index.php?option=com_content&view=article&id=108:ps1-export-command-for-git&catid=45:general&Itemid=96
    # I tweaked it to work on UBUNTU 11.04 & 11.10 plus made it mo' better
    PS1="$BIBlue$Hostname $Yellow$PathShort$Reset"'$(git branch &>/dev/null;\
    if [ $? -eq 0 ]; then \
      echo "$(echo `git status` | grep "nothing to commit" > /dev/null 2>&1; \
      if [ "$?" -eq "0" ]; then \
        # @4 - Clean repository - nothing to commit
        echo "'$Green'"$(__git_ps1 " (%s)"); \
      else \
        # @5 - Changes to working tree
        echo "'$IRed'"$(__git_ps1 " {%s}"); \
      fi) '$Reset$Prompt$Reset' "; \
    else \
      # @2 - Prompt when not in GIT repo
      echo " '$Reset$Prompt$Reset' "; \
    fi)'
}
PROMPT_COMMAND=__prompt_command

