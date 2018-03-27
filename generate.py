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
    'WG_JOBS_NUMBER',
    'WG_ERROR_CODE',
    'WG_GIT_BRANCH',
    'WG_GIT_MARKER'
]

F_DEFAULT_CLR = "9m"
F_BOLD        = "\e[1m"
F_ITALIC      = "\e[3m"
F_BG          = "\e[4"
F_FG          = "\e[3"
F_END         = "\e[0m"

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
    def __init__(self, dct):
        self.name = dct.get('type')
        self.fg = convert_color(dct.get('fg', 9))
        self.bg = convert_color(dct.get('bg', 9))
        self.fmt = convert_formatting(dct.get('fmt', ''))
        self.term = dct.get('term', '')
        self.is_static = True

    def gen_transition(self):
        return f'${{{self.name}_TRANSITION}}'

    def gen_content(self, prev_transition):
        return f'${{{self.name}_CONTENT}}'

class DynamicWidget(Widget):
    def __init__(self, dct):
        super().__init__(dct)
        self.is_static = False

class WgSshMarker(Widget):
    def __init__(self, dct):
        super().__init__(dct)
        self.marker = dct.get('extra', '')

    def gen_precondition(self, prev_transition):
        preformat = f'{F_BG}{self.bg}{prev_transition}{F_FG}{self.fg}{self.fmt}\]'
        postformat = f'\[{F_END}'
        code = f'''\
            if [ -n "${{SSH_TTY}}" ]; then
                {self.name}_CONTENT="{preformat}{self.marker}{postformat}"
                {self.name}_TRANSITION="{F_FG}{self.bg}\]{self.term}\["
            else
                {self.name}_CONTENT=""
                {self.name}_TRANSITION="{prev_transition}"
            fi\n'''
        return indent(code, -12)


class WgSshAddress(Widget):
    def gen_precondition(self, prev_transition):
        preformat = f'{F_BG}{self.bg}{prev_transition}{F_FG}{self.fg}{self.fmt}\]'
        postformat = f'\[{F_END}'
        code = f'''\
            SSH_ADDRESS=$(echo ${{SSH_CONNECTION}} | sed -r 's/\S+ \S+ (\S+) \S+/\1/')
            if [ -n "${{SSH_ADDRESS}}" ]; then
                {self.name}_CONTENT="{preformat} ${{SSH_ADDRESS}} {postformat}"
                {self.name}_TRANSITION="{F_FG}{self.bg}\]{self.term}\["
            else
                {self.name}_CONTENT=""
                {self.name}_TRANSITION="{prev_transition}"
            fi\n'''
        return indent(code, -12)


class WgUserMarker(Widget):
    def __init__(self, dct):
        super().__init__(dct)
        self.content = ' \\$ '
        self.root_bg = dct.get('extra', {}).get('bg', 9)
        self.root_fg = dct.get('extra', {}).get('fg', 9)

    def gen_transition(self):
        return f'{F_FG}${{USER_BG}}\]{self.term}\['

    def gen_content(self, prev_transition):
        preformat = f'{F_BG}${{USER_BG}}{prev_transition}{F_FG}${{USER_FG}}{self.fmt}\]'
        postformat = f'\[{F_END}'
        return f'{preformat}{self.content}{postformat}'

    def gen_precondition(self, prev_transition):
        code = f'''\
            if [ ${{UID}} -eq 0 ]; then
                USER_BG="{self.root_bg}"
                USER_FG="{self.root_fg}"
            else
                USER_BG="{self.bg}"
                USER_FG="{self.fg}"
            fi\n'''
        return indent(code, -12)


class WgUserName(WgUserMarker):
    def __init__(self, dct):
        super().__init__(dct)
        self.content = ' \\u '


class WgCustom(Widget):
    def __init__(self, dct):
        super().__init__(dct)
        self.content = dct.get('extra', '')

    def gen_transition(self):
        return f'{F_FG}{self.bg}\]{self.term}\['

    def gen_content(self, prev_transition):
        if len(self.content) == 0 and len(prev_transition) == 0:
            return ''
        else:
            preformat = f'{F_BG}{self.bg}{prev_transition}{F_FG}{self.fg}{self.fmt}\]'
            postformat = f'\[{F_END}'
            return f'{preformat}{self.content}{postformat}'

    def gen_precondition(self, prev_transition):
        return ''


class WgJobsNumber(DynamicWidget):
    def gen_precondition(self, prev_transition):
        preformat = f'{F_BG}{self.bg}{prev_transition}{F_FG}{self.fg}{self.fmt}\]'
        postformat = f'\[{F_END}'
        code = f'''\
            JOBS_NUM=$(jobs | wc -l)
            if [ ${{JOBS_NUM}} -gt 0 ]; then
                {self.name}_CONTENT="{preformat} ${{JOBS_NUM}} {postformat}"
                {self.name}_TRANSITION="{F_FG}{self.bg}{self.term}"
            else
                {self.name}_CONTENT=""
                {self.name}_TRANSITION="{prev_transition}"
            fi\n'''
        return indent(code, -12)


class WgErrorCode(DynamicWidget):
    def gen_precondition(self, prev_transition):
        preformat = f'{F_BG}{self.bg}{prev_transition}{F_FG}{self.fg}{self.fmt}\]'
        postformat = f'\[{F_END}'
        code = f'''\
            if [ ${{ERR_CODE}} -ne 0 ]; then
                {self.name}_CONTENT="{preformat} ${{ERR_CODE}} {postformat}"
                {self.name}_TRANSITION="{F_FG}{self.bg}{self.term}"
            else
                {self.name}_CONTENT=""
                {self.name}_TRANSITION="{prev_transition}"
            fi\n'''
        return indent(code, -12)


class WgGitBranch(DynamicWidget):
    def gen_precondition(self, prev_transition):
        preformat = f'{F_BG}{self.bg}{prev_transition}{F_FG}{self.fg}{self.fmt}\]'
        postformat = f'\[{F_END}'
        code = f'''\
            GIT_STATUS=$(git status --porcelain -b 2> /dev/null)
            if [ $? -eq 0 ]; then
                GIT_BRANCH=$(echo ${{GIT_STATUS}} | sed -rn '1s/## (\S+?)\.{{3}}.*/\1/p')
                {self.name}_CONTENT="{preformat} ${{GIT_BRANCH}} {postformat}"
                {self.name}_TRANSITION="{F_FG}{self.bg}{self.term}"
            else
                {self.name}_CONTENT=""
                {self.name}_TRANSITION="{prev_transition}"
            fi\n'''
        return indent(code, -12)


class WgGitMarker(DynamicWidget):
    def __init__(self, dct):
        super().__init__(dct)
        self.marker = dct.get('extra', '')

    def gen_precondition(self, prev_transition):
        preformat = f'{F_BG}{self.bg}{prev_transition}{F_FG}{self.fg}{self.fmt}\]'
        postformat = f'\[{F_END}'
        code = f'''\
            if git status &> /dev/null; then
                {self.name}_CONTENT="{preformat}{self.marker}{postformat}"
                {self.name}_TRANSITION="{F_FG}{self.bg}{self.term}"
            else
                {self.name}_CONTENT=""
                {self.name}_TRANSITION="{prev_transition}"
            fi\n'''
        return indent(code, -12)

def create_widget(dct):
    widget = None
    type = dct.get('type')
    if type == 'WG_SSH_MARKER':
        widget = WgSshMarker(dct)
    elif type == 'WG_SSH_ADDRESS':
        widget = WgSshAddress(dct)
    elif type == 'WG_USER_MARKER':
        widget = WgUserMarker(dct)
    elif type == 'WG_USER_NAME':
        widget = WgUserName(dct)
    elif type == 'WG_CUSTOM':
        widget = WgCustom(dct)
    elif type == 'WG_JOBS_NUMBER':
        widget = WgJobsNumber(dct)
    elif type == 'WG_ERROR_CODE':
        widget = WgErrorCode(dct)
    elif type == 'WG_GIT_BRANCH':
        widget = WgGitBranch(dct)
    elif type == 'WG_GIT_MARKER':
        widget = WgGitMarker(dct)
    else:
        raise RuntimeError(f'Wrong widget type: {type}.\nSupported types: {str(widget_types)}')
    return widget


class Prompt:
    def __init__(self, name, dct):
        self.name = name
        self.left = [create_widget(wg_dct) for wg_dct in dct.get('left', [])]
        self.right = [create_widget(wg_dct) for wg_dct in dct.get('right', [])]

    def static_only(self):
        return all(map(lambda x: x.is_static, self.left + self.right))

    def gen_preconditions(self):
        static = ''
        dynamic = ''
        last_transition = ''
        for widget in self.left:
            if widget.is_static:
                static += widget.gen_precondition(last_transition)
            else:
                dynamic += widget.gen_precondition(last_transition)
            last_transition = widget.gen_transition()
        return (static, dynamic)

    def gen_prompt(self):
        code = '\['
        last_transition = ''
        for widget in self.left:
            code += widget.gen_content(last_transition)
            last_transition = widget.gen_transition()
        code += f'{self.left[-1].gen_transition()}{F_END}\] '
        return code


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
            preconditions = ps.gen_preconditions()
            static_code += preconditions[0]
            dynamic_code += preconditions[1]
            if ps.static_only():
                static_code += f'\nexport {ps.name}="{ps.gen_prompt()}"'
            else:
                dynamic_code += f'\nexport {ps.name}="{ps.gen_prompt()}"'

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
