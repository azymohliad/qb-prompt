#!/bin/bash

# This file is generated automatically by qb-prompt/generate.py
# It is not recommended to edit it manually

# Apply only if terminal supports 8-bit colors 
if [ "${TERM}" != "xterm-256color" ]; then
    echo "qb-prompt: terminal does not support 8-bit colors"
else

    if [ ${UID} -eq 0 ]; then
        USER_BG="8;5;130m"
        USER_FG="7m"
    else
        USER_BG="8;5;70m"
        USER_FG="7m"
    fi
    
    SSH_ADDRESS=$(echo "${SSH_CONNECTION}" | sed -r "s/\S+ \S+ (\S+) \S+/\1/")
    if [ -n "${SSH_ADDRESS}" ]; then
        
        WG_SSH_ADDRESS_CONTENT="\e[30m\e[48;5;220m\] 🗗 ${SSH_ADDRESS} \[\e[0m\e[48;5;220m\e[0m"
        WG_SSH_ADDRESS_TRANSITION="\e[38;5;220m\]\["
        WG_SSH_ADDRESS_LEN="$((${#SSH_ADDRESS} + 5))"
    else
        
        WG_SSH_ADDRESS_CONTENT=""
        WG_SSH_ADDRESS_TRANSITION=""
        WG_SSH_ADDRESS_LEN=0
    fi
    
    export PS2="\[\e[38;5;241m\]\[\e[0m \]"
    export PS3="\[\e[38;5;241m\]\[\e[0m \]"
    export PS4="\[\e[48;5;241m\e[39m\]+\[\e[0m\e[38;5;241m\]\[\e[0m \]"

    export PROMPT_COMMAND='
        ERR_CODE=$?
        JOBS_NUM=$(jobs | wc -l)
        if [ ${JOBS_NUM} -gt 0 ]; then
            
            WG_JOBS_NUMBER_CONTENT="\e[48;5;130m\e[38;5;241m\]\[\e[37m\] ${JOBS_NUM} \[\e[0m"
            WG_JOBS_NUMBER_TRANSITION="\e[38;5;130m\]\["
            
        else
            
            WG_JOBS_NUMBER_CONTENT=""
            WG_JOBS_NUMBER_TRANSITION="\e[38;5;241m\]\["
            
        fi
        
        if [ ${ERR_CODE} -ne 0 ]; then
            
            WG_ERROR_CODE_CONTENT="\e[48;5;52m${WG_JOBS_NUMBER_TRANSITION}\e[37m\] ${ERR_CODE} \[\e[0m"
            WG_ERROR_CODE_TRANSITION="\e[38;5;52m\]\["
            
        else
            
            WG_ERROR_CODE_CONTENT=""
            WG_ERROR_CODE_TRANSITION="${WG_JOBS_NUMBER_TRANSITION}"
            
        fi
        GIT_STATUS=$(git status --porcelain -b 2> /dev/null)
        if [ $? -eq 0 ]; then
            GIT_BRANCH=$(echo "${GIT_STATUS}" | head -1 | sed -r "s/## (\S+?)\.{3}.*/\1/")
            WG_GIT_BRANCH_CONTENT="\e[37m\e[48;5;241m\]  ${GIT_BRANCH} \[\e[0m\e[48;5;241m${WG_SSH_ADDRESS_TRANSITION}\e[0m"
            WG_GIT_BRANCH_TRANSITION="\e[38;5;241m\]\["
            WG_GIT_BRANCH_LEN="$((${#GIT_BRANCH} + 5))"
        else
            
            WG_GIT_BRANCH_CONTENT=""
            WG_GIT_BRANCH_TRANSITION="${WG_SSH_ADDRESS_TRANSITION}"
            WG_GIT_BRANCH_LEN=0
        fi
        
        export PS1="\[\e[s\e[$((${COLUMNS}-${WG_SSH_ADDRESS_LEN}-${WG_GIT_BRANCH_LEN}))C${WG_GIT_BRANCH_TRANSITION}${WG_GIT_BRANCH_CONTENT}${WG_SSH_ADDRESS_CONTENT}\e[u\e[4${USER_BG}\e[3${USER_FG}\e[1m\] \$ \[\e[0m\e[48;5;241m\e[3${USER_BG}\]\[\e[37m\] $(echo "${PWD}" | sed -r "s|^${HOME}|~|;s|^(/?(\w\|[^/])+/)(.{$((${COLUMNS}/8)),})(/(\w\|[^/])+)$|\1...\4|;s|^/(.)|//\1|;s|(.)/|\1\\\\[\\\\e[38;5;246m\\\\]  \\\\[\\\\e[37m\\\\]|g") \[\e[0m${WG_JOBS_NUMBER_CONTENT}${WG_ERROR_CODE_CONTENT}${WG_ERROR_CODE_TRANSITION}\e[0m \]"'
fi
