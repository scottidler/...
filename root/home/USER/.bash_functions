# vim: filetype=sh

function int2ip() {
    ifconfig ${1:-wlp2s0} | grep 'inet addr' | sed -e 's/:/ /' | awk '{print $3}'
}

function reponame() {
    REPONAME=`git config --get remote.origin.url | sed -E 's;^(git|ssh|https)://([A-Za-z0-9\-\_]+@)?([A-Za-z0-9\.]+)/;;'`
    echo "${REPONAME%.git}"
}

function cdp() {
    if `git rev-parse`; then
        REPONAME=`reponame`
        REPOROOT=`git rev-parse --show-toplevel`
        if [[ "$REPOROOT" == *"$REPONAME" ]]; then
            PARENT="${REPOROOT%$REPONAME}"
        else
            PARENT=`dirname $REPOROOT`
        fi
        cd $PARENT
    fi
}

function cdr() {
    if `git rev-parse`; then
        cd `git rev-parse --show-toplevel`
    fi
}

function cdrr() {
    cdr
    if `git rev-parse`; then
        cd ../
    fi
    cdr
}

function upsearch() {
    FILE="$1"
    DIR="$PWD"
    while [[ "$DIR" != '/' ]]; do
        if [[ -e "$DIR/$FILE" ]]; then
            echo "$DIR"
            return
        else
            DIR=`dirname $DIR`
        fi
    done
    echo "$PWD"
    return
}

function doit() {
    (cd "`upsearch dodo.py`" && time "`which doit`" "$@")
}

