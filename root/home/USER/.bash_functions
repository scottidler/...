
function int2ip() {
    ifconfig ${1:-wlp2s0} | grep 'inet addr' | sed -e 's/:/ /' | awk '{print $3}'
}

