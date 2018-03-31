#!/usr/bin/env python

import re
import json

# Widget types definitions
widget_types = [
    'WG_SSH_MARKER',
    'WG_SSH_ADDRESS',
    'WG_USER_MARKER',
    'WG_USER_NAME',
    'WG_CUSTOM',
    'WG_CURRENT_DIR',
    'WG_JOBS_NUMBER',
    'WG_ERROR_CODE',
    'WG_GIT_BRANCH',
    'WG_GIT_MARKER'
]

DEFAULT_BG_COLOR = 9
DEFAULT_FG_COLOR = 9
DEFAULT_FORMATTING = ''
DEFAULT_TERMINATOR = ''
DEFAULT_PREFIX = ' '
DEFAULT_SUFIX = ' '
DEFAULT_CONTENT = ''

F_BOLD           = "\e[1m"
F_ITALIC         = "\e[3m"
F_BG             = "\e[4"
F_FG             = "\e[3"
F_END            = "\e[0m"
F_SAVE_CURSOR    = "\e[s"
F_RESTORE_CURSOR = "\e[u"
F_MOVE_CURSOR_B  = "\e["
F_MOVE_CURSOR_E  = "C"


def convert_color(clr):
    return f'{"" if clr < 16 else "8;5;"}{clr}m'

def convert_formatting(fmt):
    code = ''
    if fmt.find('b') != -1: code += F_BOLD
    if fmt.find('i') != -1: code += F_ITALIC
    return code

def indent(code, size):
    if size < 0:
        return ''.join(line[-size:] for line in code.splitlines(True))
    else:
        return ''.join(' '*size + line for line in code.splitlines(True))

# Classes
class Widget:
    def __init__(self, dct, is_right_aligned):
        self.name = dct.get('type')
        self.fg = convert_color(dct.get('fg', DEFAULT_FG_COLOR))
        self.bg = convert_color(dct.get('bg', DEFAULT_BG_COLOR))
        self.fmt = convert_formatting(dct.get('fmt', DEFAULT_FORMATTING))
        self.term = dct.get('term', DEFAULT_TERMINATOR)
        self.prefix = dct.get('prefix', DEFAULT_PREFIX)
        self.sufix = dct.get('sufix', DEFAULT_SUFIX)
        self.content = dct.get('content', DEFAULT_CONTENT)
        self.is_right_aligned = is_right_aligned

        self.static_length = len(self.term) + len(self.prefix) + len(self.sufix)
        self.printable = ''
        self.pre_conditional_code = ''
        self.condition_code = ':'
        self.conditional_success_code = ''
        self.conditional_fail_code = ''

    def get_content(self, prev_transition):
        if self.is_right_aligned:
            code = f'{F_FG}{self.fg}{F_BG}{self.bg}{self.fmt}\]{self.printable}'\
                   f'\[{F_END}{F_BG}{self.bg}{prev_transition}{F_END}'
        else:
            code = f'{F_BG}{self.bg}{prev_transition}{F_FG}{self.fg}{self.fmt}\]'\
                   f'{self.printable}\[{F_END}'
        return code

    def get_printable_length(self): return len(self.printable) + len(self.term)

    def get_printable_length_definitions(self):
        printable_length = self.get_printable_length()
        if self.is_right_aligned and not isinstance(printable_length, int):
            length_definition_visible = f'{self.name}_LEN="{self.get_printable_length()}"\n'
            length_definition_hidden = f'{self.name}_LEN=0\n'
            return (length_definition_visible, length_definition_hidden)
        else:
            return ('', '')


    def generate_printable_length_code(self): return f'${{{self.name}_LEN}}'

    def generate_transition_code(self): return f'${{{self.name}_TRANSITION}}'

    def generate_content_code(self, prev_transition): return f'${{{self.name}_CONTENT}}'

    def generate_init_code(self, prev_transition):
        length_definition_visible, length_definition_hidden = self.get_printable_length_definitions()
        code = f'''\
            {self.pre_conditional_code}
            if {self.condition_code}; then
                {self.conditional_success_code}
                {self.name}_CONTENT="{self.get_content(prev_transition)}"
                {self.name}_TRANSITION="{F_FG}{self.bg}\]{self.term}\["
                {length_definition_visible}
            else
                {self.conditional_fail_code}
                {self.name}_CONTENT=""
                {self.name}_TRANSITION="{prev_transition}"
                {length_definition_hidden}
            fi
            '''
        return indent(code, -12)

class StaticWidget(Widget): is_static = True

class DynamicWidget(Widget): is_static = False

class WgSshMarker(StaticWidget):
    def __init__(self, dct, is_right_aligned):
        super().__init__(dct, is_right_aligned)
        self.printable = self.prefix + self.content + self.sufix
        self.condition_code = '[ -n "${SSH_TTY}" ]'

    def generate_printable_length_code(self): return self.get_printable_length()

class WgSshAddress(StaticWidget):
    def __init__(self, dct, is_right_aligned):
        super().__init__(dct, is_right_aligned)
        self.printable = f'{self.prefix}${{SSH_ADDRESS}}{self.sufix}'
        self.pre_conditional_code = 'SSH_ADDRESS=$(echo "${SSH_CONNECTION}" | sed -r "s/\S+ \S+ (\S+) \S+/\\1/")'
        self.condition_code = '[ -n "${SSH_ADDRESS}" ]'

    def get_printable_length(self): return f'$((${{#SSH_ADDRESS}} + {self.static_length}))'

class WgUserMarker(StaticWidget):
    def __init__(self, dct, is_right_aligned):
        super().__init__(dct, is_right_aligned)
        self.printable = self.prefix + '\\$' + self.sufix
        self.root_bg = convert_color(dct.get('secondary_bg', DEFAULT_BG_COLOR))
        self.root_fg = convert_color(dct.get('secondary_fg', DEFAULT_FG_COLOR))

    def get_content(self, prev_transition):
        if self.is_right_aligned:
            code = f'{F_BG}${{USER_BG}}{F_FG}${{USER_FG}}{self.fmt}\]{self.printable}'\
                   f'\[{F_END}{F_BG}${{USER_BG}}{prev_transition}{F_END}'
        else:
            code = f'{F_BG}${{USER_BG}}{prev_transition}{F_FG}${{USER_FG}}{self.fmt}\]'\
                   f'{self.printable}\[{F_END}'
        return code

    def get_printable_length(self): return self.static_length + 1

    def generate_printable_length_code(self): return self.get_printable_length()

    def generate_transition_code(self): return f'{F_FG}${{USER_BG}}\]{self.term}\['

    def generate_content_code(self, prev_transition): return self.get_content(prev_transition)

    def generate_init_code(self, prev_transition):
        code = f'''\
            if [ ${{UID}} -eq 0 ]; then
                USER_BG="{self.root_bg}"
                USER_FG="{self.root_fg}"
            else
                USER_BG="{self.bg}"
                USER_FG="{self.fg}"
            fi
            {self.get_printable_length_definitions()[0]}
            '''
        return indent(code, -12)

class WgUserName(WgUserMarker):
    def __init__(self, dct, is_right_aligned):
        super().__init__(dct, is_right_aligned)
        self.printable = self.prefix + '\\u' + self.sufix

    def get_printable_length(self): return f'$((${{#USER}} + {self.static_length}))'

    def generate_printable_length_code(self): return f'${{{self.name}_LEN}}'

class WgCustom(StaticWidget):
    def __init__(self, dct, is_right_aligned):
        super().__init__(dct, is_right_aligned)
        self.printable = self.prefix + self.content + self.sufix
        self.length = dct.get('length', len(self.printable))

    def get_printable_length(self): 
        if isinstance(self.length, int):
            return self.length + self.static_length
        else:
            return f'$(({self.length} + {self.static_length}))'

    def generate_printable_length(self):
        if isinstance(self.length, int):
            return self.get_printable_length()
        else:
            return f'${{{self.name}_LEN}}'

    def generate_transition_code(self): return f'{F_FG}{self.bg}\]{self.term}\['

    def generate_content_code(self, prev_transition):
        if len(self.printable) == 0 and len(prev_transition) == 0:
            return ''
        else:
            return self.get_content(prev_transition)

    def generate_init_code(self, prev_transition):
        return self.get_printable_length_definitions()[0]

class WgCurrentDir(DynamicWidget):
    def __init__(self, dct, is_right_aligned):
        super().__init__(dct, is_right_aligned)
        self.separator_fg = convert_color(dct.get('secondary_fg', DEFAULT_FG_COLOR))
        self.limiter = dct.get('limiter', '$((${COLUMNS}/8))')
        self.separator = dct.get('separator')

    def get_printable_length(self): return 0

    def generate_transition_code(self): return f'{F_FG}{self.bg}\]{self.term}\['

    def generate_content_code(self, prev_transition):
        sed_scripts = []
        sed_replace_home = 's|^${HOME}|~|'
        sed_scripts.append(sed_replace_home)
        if self.limiter != None:
            sed_shorten = f's|^(/?(\w\|[^/])+/)(.{{{self.limiter},}})(/(\w\|[^/])+)$|\\1...\\4|'
            sed_scripts.append(sed_shorten)
        if self.separator != None:
            separator_color = f'\\\\\\\\[\\\\\\{F_FG}{self.separator_fg}\\\\\\\\]'
            content_color = f'\\\\\\\\[\\\\\\{F_FG}{self.fg}\\\\\\\\]' 
            sed_replace_separators = f's|^/(.)|//\\1|;s|(.)/|\\1{separator_color}{self.separator}{content_color}|g'
            sed_scripts.append(sed_replace_separators)
        sed_scripts = ';'.join(sed_scripts)
        self.content = f'$(echo "${{PWD}}" | sed -r "{sed_scripts}")'
        self.printable = self.prefix + self.content + self.sufix
        return f'{self.get_content(prev_transition)}'

    def generate_init_code(self, prev_transition):
        return ''

class WgJobsNumber(DynamicWidget):
    def __init__(self, dct, is_right_aligned):
        super().__init__(dct, is_right_aligned)
        self.printable = f'{self.prefix}${{JOBS_NUM}}{self.sufix}'
        self.pre_conditional_code = 'JOBS_NUM=$(jobs | wc -l)'
        self.condition_code = '[ ${JOBS_NUM} -gt 0 ]'
    
    def get_printable_length(self): return f'$((${{#JOBS_NUM}} + {self.static_length}))'

class WgErrorCode(DynamicWidget):
    def __init__(self, dct, is_right_aligned):
        super().__init__(dct, is_right_aligned)
        self.printable = f'{self.prefix}${{ERR_CODE}}{self.sufix}'
        self.condition_code = '[ ${ERR_CODE} -ne 0 ]'

    def get_printable_length(self): return f'$((${{#ERR_CODE}} + {self.static_length}))'

class WgGitBranch(DynamicWidget):
    def __init__(self, dct, is_right_aligned):
        super().__init__(dct, is_right_aligned)
        self.printable = f'{self.prefix}${{GIT_BRANCH}}{self.sufix}'
        self.pre_conditional_code = 'GIT_STATUS=$(git status --porcelain -b 2> /dev/null)'
        self.conditional_success_code = 'GIT_BRANCH=$(echo "${GIT_STATUS}" | head -1 | sed -r "s/## (\S+?)\.{3}.*/\\1/")'
        self.condition_code = '[ $? -eq 0 ]'

    def get_printable_length(self): return f'$((${{#GIT_BRANCH}} + {self.static_length}))'

class WgGitMarker(DynamicWidget):
    def __init__(self, dct, is_right_aligned):
        super().__init__(dct, is_right_aligned)
        self.printable = self.prefix + self.content + self.sufix
        self.condition_code = 'git status &> /dev/null'

    def gen_printable_length_code(self): return self.get_printable_length()

def create_widget(dct, is_right_aligned):
    widget = None
    widget_type = dct.get('type')
    if widget_type == 'WG_SSH_MARKER':
        widget = WgSshMarker(dct, is_right_aligned)
    elif widget_type == 'WG_SSH_ADDRESS':
        widget = WgSshAddress(dct, is_right_aligned)
    elif widget_type == 'WG_USER_MARKER':
        widget = WgUserMarker(dct, is_right_aligned)
    elif widget_type == 'WG_USER_NAME':
        widget = WgUserName(dct, is_right_aligned)
    elif widget_type == 'WG_CUSTOM':
        widget = WgCustom(dct, is_right_aligned)
    elif widget_type == 'WG_CURRENT_DIR':
        widget = WgCurrentDir(dct, is_right_aligned)
    elif widget_type == 'WG_JOBS_NUMBER':
        widget = WgJobsNumber(dct, is_right_aligned)
    elif widget_type == 'WG_ERROR_CODE':
        widget = WgErrorCode(dct, is_right_aligned)
    elif widget_type == 'WG_GIT_BRANCH':
        widget = WgGitBranch(dct, is_right_aligned)
    elif widget_type == 'WG_GIT_MARKER':
        widget = WgGitMarker(dct, is_right_aligned)
    else:
        raise RuntimeError(f'Wrong widget type: {widget_type}.\nSupported types: {str(widget_types)}')
    return widget


class Prompt:
    def __init__(self, name, dct):
        self.name = name
        self.left = [create_widget(wg_dct, False) for wg_dct in dct.get('left', [])]
        self.right = [create_widget(wg_dct, True) for wg_dct in dct.get('right', [])]

    def static_only(self):
        return all(map(lambda x: x.is_static, self.left + self.right))

    def generate_init_codes(self, right_aligned):
        static_init_code = ''
        dynamic_init_code = ''
        last_transition = ''
        widgets = self.right if right_aligned else self.left
        for widget in widgets:
            if widget.is_static:
                static_init_code += widget.generate_init_code(last_transition)
            else:
                dynamic_init_code += widget.generate_init_code(last_transition)
            last_transition = widget.generate_transition_code()
        return (static_init_code, dynamic_init_code)

    def generate_content_code(self):
        left_prompt = ''
        if len(self.left) > 0:
            last_transition = ''
            for widget in self.left:
                left_prompt += widget.generate_content_code(last_transition)
                last_transition = widget.generate_transition_code()
            left_prompt += self.left[-1].generate_transition_code() + F_END

        right_prompt = ''
        if len(self.right) > 0:
            last_transition = ''
            printable_lengths = []
            printable_length_num = 0
            for widget in self.right:
                right_prompt = widget.generate_content_code(last_transition) + right_prompt
                last_transition = widget.generate_transition_code()
                printable_length = widget.generate_printable_length_code()
                if isinstance(printable_length, int):
                    printable_length_num += printable_length
                else:
                    printable_lengths.append(printable_length)
            if printable_length_num > 0:
                printable_lengths.append(str(printable_length_num))
            printable_length = '-'.join(printable_lengths)
            right_prompt = self.right[-1].generate_transition_code() + right_prompt
            right_prompt = f'{F_SAVE_CURSOR}{F_MOVE_CURSOR_B}$((${{COLUMNS}}-{printable_length})){F_MOVE_CURSOR_E}{right_prompt}{F_RESTORE_CURSOR}'
        return f'\[{right_prompt}{left_prompt} \]'


class Prompts:
    def __init__(self, dct):
        self.ps1 = Prompt('PS1', dct.get('PS1'))
        self.ps2 = Prompt('PS2', dct.get('PS2'))
        self.ps3 = Prompt('PS3', dct.get('PS3'))
        self.ps4 = Prompt('PS4', dct.get('PS4'))

    def generate(self):
        static_code = ''
        dynamic_code = ''

        for ps in [self.ps1, self.ps2, self.ps3, self.ps4]:
            preconditions = ps.generate_init_codes(False)
            static_code += preconditions[0]
            dynamic_code += preconditions[1]
            preconditions = ps.generate_init_codes(True)
            static_code += preconditions[0]
            dynamic_code += preconditions[1]

            if ps.static_only():
                static_code += f'\nexport {ps.name}="{ps.generate_content_code()}"'
            else:
                dynamic_code += f'\nexport {ps.name}="{ps.generate_content_code()}"'

        if len(dynamic_code) > 0:
            dynamic_code=f'''\
                export PROMPT_COMMAND='
                    ERR_CODE=$?\n{indent(dynamic_code, 20)}'\n'''

        code = f'''\
            #!/bin/bash
            
            # This file is generated automatically by qb-prompt/generate.py
            # It is not recommended to edit it manually
            
            # Apply only if terminal supports 8-bit colors 
            if [ "${{TERM}}" != "xterm-256color" ]; then
                echo "qb-prompt: terminal does not support 8-bit colors"
            else
            \n{indent(static_code, 16)}
            \n{dynamic_code}
            fi'''

        return indent(code, -12)




# --- ENTRY POINT ----------------------------------------------------------------------------------

# Read config file
with open('conf.json') as conf:
    config = conf.read()

# Create objects
prompts_json = json.loads(re.sub(r'//.*', '', config))

try:
    prompts = Prompts(prompts_json)
except RuntimeError as error:
    print('Failed to parse config.json:\n' + str(error))
    exit(-1)

print(prompts.generate())
