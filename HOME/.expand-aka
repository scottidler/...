#!/bin/zsh

log() {
  if [[ -n $AKA_LOG ]]; then
    echo "$@" >> ~/aka.txt
  fi
}

# Expands a keyword into a longer command using `aka query` upon pressing space
expand-aka-space() {
    if [ ! -f ~/aka-killswitch ]; then
        log "expand-aka-space: BUFFER=$BUFFER"
        OUTPUT=$(aka query "$BUFFER")
        RC=$?
        log "expand-aka-space: OUTPUT=$OUTPUT"
        if [ $RC -ne 0 ]; then
            echo "RC=$RC"
        fi
        if [ -n "$OUTPUT" ]; then
            BUFFER="$OUTPUT"
            log "expand-aka-space: CURSOR=$CURSOR"
            CURSOR=$(expr length "$BUFFER")
            log "expand-aka-space: CURSOR(after assignment)=$CURSOR"
        else
            zle self-insert
        fi
    else
        zle self-insert
    fi
}
zle -N expand-aka-space
bindkey " " expand-aka-space
bindkey -M isearch " " magic-space

# Expands a keyword into a longer command using `aka --eol query` before executing the command
expand-aka-accept-line() {
    if [ ! -f ~/aka-killswitch ]; then
        log "expand-aka-accept-line: BUFFER=$BUFFER"
        OUTPUT=$(aka --eol query "$BUFFER")
        RC=$?
        log "expand-aka-accept-line: OUTPUT=$OUTPUT"
        if [ $RC -ne 0 ]; then
            echo "RC=$RC"
        fi
        if [ -n "$OUTPUT" ]; then
            BUFFER="$OUTPUT"
            log "expand-aka-accept-line: CURSOR=$CURSOR"
            CURSOR=$(expr length "$BUFFER")
            log "expand-aka-accept-line: CURSOR(after assignment)=$CURSOR"
        fi
        zle .accept-line
    else
        zle .accept-line
    fi
}
zle -N accept-line expand-aka-accept-line

# Adds a trailing space to every command line before it's stored in history
function add-space-to-command() {
    if [[ "${BUFFER: -1}" != " " ]]; then
        BUFFER+=" "
        CURSOR=$#BUFFER
    fi
}
zle -N zle-line-finish add-space-to-command

# Recalls previous command from history and ensures it ends with a space upon pressing up-arrow
function up-line-or-add-space() {
    zle up-line-or-history
    [[ $LBUFFER != *' '* ]] && zle backward-delete-char
    LBUFFER+=' '
}
zle -N up-line-or-add-space
bindkey '^[[A' up-line-or-add-space

# Define a function to search through aka aliases
aka-search() {
    # Run 'aka ls', pipe the output to fzf
    local alias=$(aka ls | sk --prompt "aka> ")

    # If an alias was selected (user didn't press escape)
    if [[ -n $alias ]]; then
        # Extract the alias name (everything before the first ':')
        local alias_name=${alias%%:*}

        # Type the alias at the command prompt
        LBUFFER+=$alias_name
    fi
}
zle -N aka-search

# Bind the function to a shortcut key
# Here we're using Ctrl+t, but you can choose a different shortcut
bindkey '^t' aka-search

