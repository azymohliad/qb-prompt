## Colors
ROOT_BG="8;5;130m"
ROOT_FG="7m"

USER_BG="8;5;106m"
USER_FG="7m"

DIR_BG="8;5;241m"
DIR_FG="7m"

## Helper vars
FMT_BOLD="\e[1m"
DEFAULT="9m"
BG="\e[4"
FG="\e[3"
END="\e[0m"

## Formattings
if [ $UID -eq 0 ]; then
	USER_FMT="${FG}${ROOT_FG}${BG}${ROOT_BG}${FMT_BOLD}"
	USER_TERM_FMT="${FG}${ROOT_BG}${BG}${DIR_BG}"
else 
	USER_FMT="${FG}${USER_FG}${BG}${USER_BG}${FMT_BOLD}"
	USER_TERM_FMT="${FG}${USER_BG}${BG}${DIR_BG}"
fi
DIR_FMT="${FG}${DIR_FG}${BG}${DIR_BG}"
DIR_TERM_FMT="${FG}${DIR_BG}${BG}${DEFAULT}"

## Prompts
export PS1="\
\[${USER_FMT}\] \u \[${END}${USER_TERM_FMT}\]\
\[${DIR_FMT}\] \w \[${DIR_TERM_FMT}\] \[${END}\]"

export PS2="\[${DIR_TERM_FMT}\] \[${END}\]"
export PS3="\[${DIR_TERM_FMT}\] \[${END}\]"
export PS4="\[${DIR_FMT}\]+\[${DIR_TERM_FMT}\] \[${END}\]"
