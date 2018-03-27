#!/bin/bash

# This file is generated automatically by qb-prompt/generate.py
# It is not recommended to edit it manually

# Apply only if terminal supports 8-bit colors 
if [ "${TERM}" != "xterm-256color" ]; then
    echo "qb-prompt: terminal does not support 8-bit colors"
else

    if [ -n "${SSH_TTY}" ]; then
        WG_SSH_MARKER_CONTENT="\e[48;5;252m\e[38;5;70m\] 🗗 \[\e[0m"
        WG_SSH_MARKER_TRANSITION="\e[38;5;252m\]\["
    else
        WG_SSH_MARKER_CONTENT=""
        WG_SSH_MARKER_TRANSITION=""
    fi
    if [ ${UID} -eq 0 ]; then
        USER_BG="130"
        USER_FG="7"
    else
        USER_BG="8;5;70m"
        USER_FG="7m"
    fi
    
    export PS2="\[\e[38;5;241m\]\[\e[0m\] "
    export PS3="\[\e[38;5;241m\]\[\e[0m\] "
    export PS4="\[\e[48;5;241m\e[39m\]+\[\e[0m\e[38;5;241m\]\[\e[0m\] "

    export PROMPT_COMMAND='
        ERR_CODE=$?
        JOBS_NUM=$(jobs | wc -l)
        if [ ${JOBS_NUM} -gt 0 ]; then
            WG_JOBS_NUMBER_CONTENT="\e[48;5;99m\e[38;5;241m\]\[\e[37m\] ${JOBS_NUM} \[\e[0m"
            WG_JOBS_NUMBER_TRANSITION="\e[38;5;99m"
        else
            WG_JOBS_NUMBER_CONTENT=""
            WG_JOBS_NUMBER_TRANSITION="\e[38;5;241m\]\["
        fi
        if [ ${ERR_CODE} -ne 0 ]; then
            WG_ERROR_CODE_CONTENT="\e[48;5;52m${WG_JOBS_NUMBER_TRANSITION}\e[37m\] ${ERR_CODE} \[\e[0m"
            WG_ERROR_CODE_TRANSITION="\e[38;5;52m"
        else
            WG_ERROR_CODE_CONTENT=""
            WG_ERROR_CODE_TRANSITION="${WG_JOBS_NUMBER_TRANSITION}"
        fi
        
        export PS1="\[${WG_SSH_MARKER_CONTENT}\e[4${USER_BG}${WG_SSH_MARKER_TRANSITION}\e[3${USER_FG}\e[1m\] \$ \[\e[0m\e[48;5;241m\e[3${USER_BG}\]\[\e[37m\e[3m\] \w \[\e[0m${WG_JOBS_NUMBER_CONTENT}${WG_ERROR_CODE_CONTENT}${WG_ERROR_CODE_TRANSITION}\e[0m\] "'
fi
