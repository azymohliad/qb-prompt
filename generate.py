#!/usr/bin/env python

import re
import json
import sys

# -- Default values --------------------------------------------------------------------------------
DEFAULT_BG_COLOR = 9
DEFAULT_FG_COLOR = 9
DEFAULT_FORMATTING = ''
DEFAULT_TERMINATOR = ''
DEFAULT_PREFIX = ' '
DEFAULT_SUFIX = ' '
DEFAULT_CONTENT = ''

DEFAULT_CONFIG_FILE = 'sample_configs/default.json'
DEFAULT_OUTPUT_FILE = 'qb-prompt.sh'

HELP = f'''\
Generate bash prompt configuration script.

Usage:
    ./generate.py [config_file|-] [output_file]
where
    config_file - input json-formatted configuration file ('-' for default). Default: "{DEFAULT_CONFIG_FILE}"
    output_file - output bash prompt configuration script. Default: "{DEFAULT_OUTPUT_FILE}"\
'''


# -- Helper variables ------------------------------------------------------------------------------
F_BOLD           = "\e[1m"
F_ITALIC         = "\e[3m"
F_BG             = "\e[4"
F_FG             = "\e[3"
F_END            = "\e[0m"
F_SAVE_CURSOR    = "\e[s"
F_RESTORE_CURSOR = "\e[u"
F_MOVE_CURSOR_B  = "\e["
F_MOVE_CURSOR_E  = "C"


# -- Helper functions ------------------------------------------------------------------------------
def convert_color(clr):
    if str(clr).isdigit() and int(clr) < 256:
        return f'{"" if int(clr) < 16 else "8;5;"}{clr}m'
    else:
        return None

def convert_formatting(fmt):
    if all([ch in 'bi' for ch in fmt]):
        code = ''
        if fmt.find('b') != -1: code += F_BOLD
        if fmt.find('i') != -1: code += F_ITALIC
        return code
    else:
        return None

def indent(code, size):
    if size < 0:
        return ''.join(line[-size:] for line in code.splitlines(True))
    else:
        return ''.join(' '*size + line for line in code.splitlines(True))


# -- Widget Classes --------------------------------------------------------------------------------
class Widget:
    def init(self, dct, is_right_aligned):
        # Read input parameters
        self.cfg = lambda: None
        self.cfg.type = dct.get('type')
        self.cfg.fg = convert_color(dct.get('fg', DEFAULT_FG_COLOR))
        self.cfg.bg = convert_color(dct.get('bg', DEFAULT_BG_COLOR))
        self.cfg.fmt = convert_formatting(dct.get('fmt', DEFAULT_FORMATTING))
        self.cfg.term = dct.get('term', DEFAULT_TERMINATOR)
        self.cfg.prefix = dct.get('prefix', DEFAULT_PREFIX)
        self.cfg.sufix = dct.get('sufix', DEFAULT_SUFIX)
        self.cfg.content = dct.get('content', DEFAULT_CONTENT)
        self.is_right_aligned = is_right_aligned
        
        # Define other fields
        self.static_length = len(self.cfg.term) + len(self.cfg.prefix) + len(self.cfg.sufix)
        self.printable = ''
        self.pre_conditional_code = ''
        self.condition_code = ':'
        self.conditional_success_code = ''
        self.conditional_fail_code = ''

    def validate(self):
        for key, val in self.cfg.__dict__.items():
            if val == None:
                raise RuntimeError(f'{self.cfg.type}: Invalid "{key}" value')

    def __init__(self, dct, is_right_aligned):
        self.init(dct, is_right_aligned)
        self.validate()

    def get_content(self, prev_transition):
        if self.is_right_aligned:
            code = f'{F_FG}{self.cfg.fg}{F_BG}{self.cfg.bg}{self.cfg.fmt}\]{self.printable}'\
                   f'\[{F_END}{F_BG}{self.cfg.bg}{prev_transition}{F_END}'
        else:
            code = f'{F_BG}{self.cfg.bg}{prev_transition}{F_FG}{self.cfg.fg}{self.cfg.fmt}\]'\
                   f'{self.printable}\[{F_END}'
        return code

    def get_printable_length(self): return len(self.printable) + len(self.cfg.term)

    def get_printable_length_definitions(self):
        printable_length = self.get_printable_length()
        if self.is_right_aligned and not isinstance(printable_length, int):
            length_definition_visible = f'{self.cfg.type}_LEN="{self.get_printable_length()}"\n'
            length_definition_hidden = f'{self.cfg.type}_LEN=0\n'
            return (length_definition_visible, length_definition_hidden)
        else:
            return ('', '')


    def generate_printable_length_code(self): return f'${{{self.cfg.type}_LEN}}'

    def generate_transition_code(self): return f'${{{self.cfg.type}_TRANSITION}}'

    def generate_content_code(self, prev_transition): return f'${{{self.cfg.type}_CONTENT}}'

    def generate_init_code(self, prev_transition):
        length_definition_visible, length_definition_hidden = self.get_printable_length_definitions()
        code = f'''\
            {self.pre_conditional_code}
            if {self.condition_code}; then
                {self.conditional_success_code}
                {self.cfg.type}_CONTENT="{self.get_content(prev_transition)}"
                {self.cfg.type}_TRANSITION="{F_FG}{self.cfg.bg}\]{self.cfg.term}\["
                {length_definition_visible}
            else
                {self.conditional_fail_code}
                {self.cfg.type}_CONTENT=""
                {self.cfg.type}_TRANSITION="{prev_transition}"
                {length_definition_hidden}
            fi
            '''
        return indent(code, -12)

class StaticWidget(Widget): is_static = True

class DynamicWidget(Widget): is_static = False


# ------ WgSshMarker -------------------------------------------------------------------------------
class WgSshMarker(StaticWidget):
    def init(self, dct, is_right_aligned):
        super().init(dct, is_right_aligned)
        self.printable = self.cfg.prefix + self.cfg.content + self.cfg.sufix
        self.condition_code = '[ -n "${SSH_TTY}" ]'

    def generate_printable_length_code(self): return self.get_printable_length()


# ------ WgSshAddress ------------------------------------------------------------------------------
class WgSshAddress(StaticWidget):
    def init(self, dct, is_right_aligned):
        super().init(dct, is_right_aligned)
        self.printable = f'{self.cfg.prefix}${{SSH_ADDRESS}}{self.cfg.sufix}'
        self.pre_conditional_code = 'SSH_ADDRESS=$(echo "${SSH_CONNECTION}" | sed -r "s/\S+ \S+ (\S+) \S+/\\1/")'
        self.condition_code = '[ -n "${SSH_ADDRESS}" ]'

    def get_printable_length(self): return f'$((${{#SSH_ADDRESS}} + {self.static_length}))'


# ------ WgUserMarker ------------------------------------------------------------------------------
class WgUserMarker(StaticWidget):
    def init(self, dct, is_right_aligned):
        super().init(dct, is_right_aligned)
        self.cfg.root_bg = convert_color(dct.get('secondary_bg', DEFAULT_BG_COLOR))
        self.cfg.root_fg = convert_color(dct.get('secondary_fg', DEFAULT_FG_COLOR))
        self.content = '\\\\$'
        self.printable = self.cfg.prefix + self.content + self.cfg.sufix

    def get_content(self, prev_transition):
        if self.is_right_aligned:
            code = f'{F_BG}${{USER_BG}}{F_FG}${{USER_FG}}{self.cfg.fmt}\]{self.printable}'\
                   f'\[{F_END}{F_BG}${{USER_BG}}{prev_transition}{F_END}'
        else:
            code = f'{F_BG}${{USER_BG}}{prev_transition}{F_FG}${{USER_FG}}{self.cfg.fmt}\]'\
                   f'{self.printable}\[{F_END}'
        return code

    def get_printable_length(self): return self.static_length + 1

    def generate_printable_length_code(self): return self.get_printable_length()

    def generate_transition_code(self): return f'{F_FG}${{USER_BG}}\]{self.cfg.term}\['

    def generate_content_code(self, prev_transition): return self.get_content(prev_transition)

    def generate_init_code(self, prev_transition):
        code = f'''\
            if [ ${{UID}} -eq 0 ]; then
                USER_BG="{self.cfg.root_bg}"
                USER_FG="{self.cfg.root_fg}"
            else
                USER_BG="{self.cfg.bg}"
                USER_FG="{self.cfg.fg}"
            fi
            {self.get_printable_length_definitions()[0]}
            '''
        return indent(code, -12)


# ------ WgUserName --------------------------------------------------------------------------------
class WgUserName(WgUserMarker):
    def init(self, dct, is_right_aligned):
        super().init(dct, is_right_aligned)
        self.printable = self.cfg.prefix + '\\u' + self.cfg.sufix

    def get_printable_length(self): return f'$((${{#USER}} + {self.static_length}))'

    def generate_printable_length_code(self): return f'${{{self.cfg.type}_LEN}}'


# ------ WgCustom ----------------------------------------------------------------------------------
class WgCustom(StaticWidget):
    def init(self, dct, is_right_aligned):
        super().init(dct, is_right_aligned)
        self.printable = self.cfg.prefix + self.cfg.content + self.cfg.sufix
        self.cfg.length = dct.get('length', len(self.printable))

    def get_printable_length(self): 
        if isinstance(self.cfg.length, int):
            return self.cfg.length + self.static_length
        else:
            return f'$(({self.cfg.length} + {self.static_length}))'

    def generate_printable_length(self):
        if isinstance(self.cfg.length, int):
            return self.get_printable_length()
        else:
            return f'${{{self.cfg.type}_LEN}}'

    def generate_transition_code(self): return f'{F_FG}{self.cfg.bg}\]{self.cfg.term}\['

    def generate_content_code(self, prev_transition):
        if len(self.printable) == 0 and len(prev_transition) == 0:
            return ''
        else:
            return self.get_content(prev_transition)

    def generate_init_code(self, prev_transition):
        return self.get_printable_length_definitions()[0]


# ------ WgCurrentDir ------------------------------------------------------------------------------
class WgCurrentDir(DynamicWidget):
    # TODO: Invent smarter shortening algorithm
    def init(self, dct, is_right_aligned):
        super().init(dct, is_right_aligned)
        self.cfg.separator_fg = convert_color(dct.get('secondary_fg', DEFAULT_FG_COLOR))
        self.cfg.separator = dct.get('separator', '/')

    def get_printable_length(self): return 0

    def generate_transition_code(self): return f'{F_FG}{self.cfg.bg}\]{self.cfg.term}\['

    def generate_content_code(self, prev_transition):
        sed_scripts = []

        sed_replace_home = 's|^${HOME}|~|'
        sed_scripts.append(sed_replace_home)

        sed_shorten = 's|^(.{,${STEP}}/)(.{${STEP},})(/.{${STEP},}$)|\\1···\\3|'
        sed_scripts.append(sed_shorten)

        if self.cfg.separator != '/':
            separator_color = f'\\\\\\\\[\\\\\\{F_FG}{self.cfg.separator_fg}\\\\\\\\]'
            content_color = f'\\\\\\\\[\\\\\\{F_FG}{self.cfg.fg}\\\\\\\\]'
            sed_replace_separators = f's|^/(.)|//\\1|;s|(.)/|\\1{separator_color}{self.cfg.separator}{content_color}|g'
            sed_scripts.append(sed_replace_separators)

        sed_scripts = ';'.join(sed_scripts)
        self.cfg.content = f'$(echo "${{PWD}}" | sed -r "{sed_scripts}")'
        self.printable = self.cfg.prefix + self.cfg.content + self.cfg.sufix
        return f'{self.get_content(prev_transition)}'

    def generate_init_code(self, prev_transition):
        code = '''
            STEP=$((${COLUMNS}/8))
        '''
        return indent(code, -12)


# ------ WgJobsNumber ------------------------------------------------------------------------------
class WgJobsNumber(DynamicWidget):
    def init(self, dct, is_right_aligned):
        super().init(dct, is_right_aligned)
        self.printable = f'{self.cfg.prefix}${{JOBS_NUM}}{self.cfg.sufix}'
        self.pre_conditional_code = 'JOBS_NUM=$(jobs | wc -l)'
        self.condition_code = '[ ${JOBS_NUM} -gt 0 ]'
    
    def get_printable_length(self): return f'$((${{#JOBS_NUM}} + {self.static_length}))'


# ------ WgErrorCode -------------------------------------------------------------------------------
class WgErrorCode(DynamicWidget):
    def init(self, dct, is_right_aligned):
        super().init(dct, is_right_aligned)
        self.printable = f'{self.cfg.prefix}${{ERR_CODE}}{self.cfg.sufix}'
        self.condition_code = '[ ${ERR_CODE} -ne 0 ]'

    def get_printable_length(self): return f'$((${{#ERR_CODE}} + {self.static_length}))'


# ------ WgGitBranch -------------------------------------------------------------------------------
class WgGitBranch(DynamicWidget):
    def init(self, dct, is_right_aligned):
        super().init(dct, is_right_aligned)
        self.printable = f'{self.cfg.prefix}${{GIT_BRANCH}}{self.cfg.sufix}'
        self.pre_conditional_code = 'GIT_BRANCH_CMD=$(git branch 2> /dev/null)'
        self.conditional_success_code = 'GIT_BRANCH=$(echo "${GIT_BRANCH_CMD}" | sed -rn "/^\*/s/\* (\S+)/\\1/p")'
        self.condition_code = '[ $? -eq 0 ]'

    def get_printable_length(self): return f'$((${{#GIT_BRANCH}} + {self.static_length}))'


# ------ WgGitMarker -------------------------------------------------------------------------------
class WgGitMarker(DynamicWidget):
    def init(self, dct, is_right_aligned):
        super().init(dct, is_right_aligned)
        self.printable = self.cfg.prefix + self.cfg.content + self.cfg.sufix
        self.condition_code = 'git status &> /dev/null'

    def gen_printable_length_code(self): return self.get_printable_length()



# -- Prompt ----------------------------------------------------------------------------------------
def create_widget(dct, is_right_aligned):
    # Widget types definitions
    widgets_dict = {
        'WG_SSH_MARKER': WgSshMarker,
        'WG_SSH_ADDRESS': WgSshAddress,
        'WG_USER_MARKER': WgUserMarker,
        'WG_USER_NAME': WgUserName,
        'WG_CUSTOM': WgCustom,
        'WG_CURRENT_DIR': WgCurrentDir,
        'WG_JOBS_NUMBER': WgJobsNumber,
        'WG_ERROR_CODE': WgErrorCode,
        'WG_GIT_BRANCH': WgGitBranch,
        'WG_GIT_MARKER': WgGitMarker
    }

    widget_type = dct.get('type')
    widget_contructor = widgets_dict.get(widget_type)

    if widget_contructor == None:
        raise RuntimeError(f'Wrong widget type: {widget_type}.\nSupported widgets:' +
                           ''.join(['\n - ' + key for key in widgets_dict.keys()]))
    else:
        return widget_contructor(dct, is_right_aligned)

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
            right_prompt = f'{F_SAVE_CURSOR}{F_MOVE_CURSOR_B}$((${{COLUMNS}}-{printable_length}))'\
                           f'{F_MOVE_CURSOR_E}{right_prompt}{F_RESTORE_CURSOR}'
        return f'\[{right_prompt}{left_prompt} \]'


# -- Prompts ---------------------------------------------------------------------------------------
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


####################################################################################################
# -- ENTRY POINT ----------------------------------------------------------------------------------#
####################################################################################################

config_file = DEFAULT_CONFIG_FILE
output_file = DEFAULT_OUTPUT_FILE
if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help']:
  print(HELP)
  exit(0)
if len(sys.argv) > 1 and sys.argv[1] != '-':
  config_file = sys.argv[1]
if len(sys.argv) > 2:
  output_file = sys.argv[2]

# Read config
try:
    with open(config_file) as file: config = file.read()
except FileNotFoundError: 
    print(f'Iput file "{config_file}" not found')
    exit(-1)
except:
    print("Failed to read input file:", sys.exc_info()[0])
    exit(-1)

# Parse config
try:
    prompts_json = json.loads(re.sub(r'//.*', '', config))
    prompts = Prompts(prompts_json)
except (json.decoder.JSONDecodeError, RuntimeError) as error:
    print(f'Failed to parse input config:\n{str(error)}')
    exit(-1)

# Generate shell script
code = prompts.generate()

# Write generated script to output file
try:
    with open(output_file, 'w') as file: file.write(code)
except:
    print("Failed to write output file:", sys.exc_info()[0])
    exit(-1)
