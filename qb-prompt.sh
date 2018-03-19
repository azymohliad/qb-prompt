#!/bin/bash

###############################################################################
################################## qb-prompt ##################################
###############################################################################

# Apply only if terminal supports 8-bit colors 
if [ "${TERM}" != "xterm-256color" ]; then
    echo "qb-prompt: terminal does not support 8-bit colors"
else

## Helper vars
F_DEFAULT_CLR="9m"
F_BOLD="\e[1m"
F_ITALIC="\e[3m"
F_BG="\e[4"
F_FG="\e[3"
F_END="\e[0m"


## CONFIGURATION ##############################################################
# Widgets
WIDGET_HOST=''      # 'H' - full | 'h' - short | '' - off
WIDGET_USER='$'     # '$' - marker | 'u' - username 
WIDGET_DIR='w'      # 'w' - full | 'W' - short

# Colors
# https://en.wikipedia.org/wiki/ANSI_escape_code#8-bit
BG_HOST="8;5;95";   FG_HOST="7"
BG_ROOT="8;5;130";  FG_ROOT="7"
BG_USER="8;5;70";   FG_USER="7"
BG_DIR="8;5;241";   FG_DIR="7"
BG_SSH="8;5;252";   FG_SSH="8;5;70"
BG_ERR="8;5;52";    FG_ERR="7"

FMT_USER="${F_BOLD}"
FMT_DIR="${F_ITALIC}"
###############################################################################


## Widgets
i=0;

# SSH indicator
if [ -n "${SSH_TTY}" ]; then
    SW_CONTENT[$i]=" 🗗 "
    SW_BG[$i]="${BG_SSH}m"
    SW_FG[$i]="${FG_SSH}m"
    SW_FMT[$i]=""
    SW_TERM[$i]=""
    ((i++))
fi

# Host
if [ -n "${WIDGET_HOST}" ]; then
    SW_CONTENT[$i]=" \\${WIDGET_HOST} "
    SW_BG[$i]="${BG_HOST}m"
    SW_FG[$i]="${FS_HOST}m"
    SW_FMT[$i]="${FMT_HOST}"
    SW_TERM[$i]=""
    ((i++))
fi

# Username
SW_CONTENT[$i]=" \\${WIDGET_USER} "
if [ ${UID} -eq 0 ]; then
    SW_BG[$i]="${BG_ROOT}m"
    SW_FG[$i]="${FG_ROOT}m"
else
    SW_BG[$i]="${BG_USER}m"
    SW_FG[$i]="${FG_USER}m"
fi
SW_FMT[$i]="${FMT_USER}"
SW_TERM[$i]=""
((i++))

# Working directory
SW_CONTENT[$i]=" \\${WIDGET_DIR} "
SW_BG[$i]="${BG_DIR}m"
SW_FG[$i]="${FG_DIR}m"
SW_FMT[$i]="${FMT_DIR}"
SW_TERM[$i]=""
((i++))

## Format static part of prompt string
SW_COUNT=$i
PROMPT_STATIC=""
for ((i=0; i<${SW_COUNT}; i++)); do
    PROMPT_STATIC="${PROMPT_STATIC}\[${SW_FMT[$i]}${F_BG}${SW_BG[$i]}${F_FG}${SW_FG[$i]}\]${SW_CONTENT[$i]}\[${F_END}\]"
    if [ $i -lt $((SW_COUNT-1)) -a -n SW_TERM[$i] ]; then
        SEPARATOR="\[${F_FG}${SW_BG[$i]}${F_BG}${SW_BG[$((i+1))]}\]${SW_TERM[$i]}\[${F_END}\]"
        PROMPT_STATIC="${PROMPT_STATIC}${SEPARATOR}"
    fi
done

export PROMPT_COMMAND='
RET=$?
i=0
if [ ${RET} -ne 0 ]; then
    DW_CONTENT[$i]=${RET}
    DW_BG[$i]="${BG_ERR}m"
    DW_FG[$i]="${FG_ERR}m"
    DW_TERM[$i]=""
    ((i++))
fi
DW_BG[$i]=${F_DEFAULT_CLR}
DW_COUNT=$i

i=$((SW_COUNT-1))
SEPARATOR="\[${F_FG}${SW_BG[$i]}${F_BG}${DW_BG[0]}\]${SW_TERM[$i]}\[${F_END}\]"
PROMPT=${PROMPT_STATIC}${SEPARATOR}
for ((i=0; $i<${DW_COUNT}; i++)); do
    SEPARATOR="\[${F_FG}${DW_BG[$i]}${F_BG}${DW_BG[$((i+1))]}\]${DW_TERM[$i]}\[${F_END}\]"
    PROMPT="${PROMPT}\[${DW_FMT[$i]}${F_BG}${DW_BG[$i]}${F_FG}${DW_FG[$i]}\]${DW_CONTENT[$i]}${SEPARATOR}"
done

export PS1="${PROMPT} "'


## Prompts
export PS2="\[${F_FG}${C_GREY}${F_BG}${F_DEFAULT_CLR}\] \[${F_END}\]"
export PS3="\[${F_FG}${C_GREY}${F_BG}${F_DEFAULT_CLR}\] \[${F_END}\]"
export PS4="\[${F_FG}${C_WHITE}${F_BG}${C_GREY}\]+\[${F_FG}${C_GREY}${F_BG}${F_DEFAULT_CLR}\] \[${F_END}\]"

fi # if [ "${TERM}" = "xterm-256color"]; then