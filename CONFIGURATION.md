# Configuration

**It might be helpfull to check `sample_configs` before reading this.**

Input config files for **qb-prompt** should be JSON-formatted and have following structure:
```
{
    "PS1": {
        "left": [
            // Left-aligned widget list
        ],
        "right": [
            // Right-aligned widget list
        ]
    },

    "PS2": {
        // Same structure as for PS1
    },

    "PS3": {
        // Same structure as for PS1
    },

    "PS4": {
        // Same structure as for PS1
    }
}
```

So basically it defines the content of prompts `PS1`, `PS2`, `PS3` and `PS4` in declarative form. You can check more about various bash prompts [here](https://www.gnu.org/software/bash/manual/bashref.html#Shell-Variables) if you are not familiar with it. In short, `PS1` is a primary prompt and is printed before each command, so it should usually contain all needed info, the rest are used in rare cases (complete unfinished command, select statement, etc).

`left` and `right` widget arrays define the widgets aligned from left side and right side respectively, in order from the edge towards oposite edge. They both are optional, empty by default. Note that right-aligned positioning is kinda hack, so it doesn't work perfectly in all cases (it shifts on resize, disappears when you remove last character of the command, wipes away if the command reaches it, etc). Don't put too many widgets on the right.

## Widget attributes

Each widget is defined using the following attributes:

Attribute | Description | Default value | Used in widgets
----------|-------------|---------------|----------------
type      | Widget type (listed below) | No (mandatory) | all
fg        | Foreground color (number 1-255) | 9         | all 
bg        | Background color (number 1-255) | 9         | all
term      | Terminator (separator between current and next widgets) | '' | all
fmt       | Additional formatting (string, where 'b' means bold, 'i' - italic) | '' | all
prefix    | Additional prefix before actual content | ' ' | all
sufix     | Additional sufix before actual content | ' ' | all
content   | Content, when widget itself does not define it | '' | WG_CUSTOM, WG_SSH_MARKER, WG_GIT_MARKER
secondary_fg | Secondary foreground color (concreete use is defined by widget) | 9 | WG_USER_NAME, WG_USER_MARKER, WG_CURRENT_DIR
secondary_bg | Secondary background color (concreete use is defined by widget) | 9 | WG_USER_NAME, WG_USER_MARKER
separator | Custom separator in path for WG_CURRENT_DIR | '' | WG_CURRENT_DIR
length | Number of characters in content. Useful for right-aligned custom widgets with non-static content | length of static content | WG_CUSTOM


Colors are represented as single 8-bit numbers, according to [this table](https://en.wikipedia.org/wiki/ANSI_escape_code#8-bit)

## Available widgets:

There are multiple different widgets available. Each adds some specific behaviour to your prompt. I divide them into two main categories: *statically dispatched* and *dynamically dispatched*. Statically dispatched widgets have the same inner values for the whole session. They may require to process some data on session login, but don't have any implicit runtime after that. Dynamically dispatched widgets process some data and optionally update their inner values every time the prompt is reprinted. They make use of special `PROMPT_COMMAND` variable to achieve that. The point of this story is that statically dispatched widgets might theoretically cause lags when you launch the terminal, and dynamically dispatched widgets may slow down the prompt reprinting.  

### WG_USER_MARKER
static dispatch
Displays '#' for root, '$' for other users. Also `root` user is decorated by `secondary_bg` and `secondary_fg` colors.

### WG_USER_NAME
static dispatch
Displays username. `root` user is decorated by `secondary_bg` and `secondary_fg` colors.

### WG_SSH_MARKER
static dispatch
Indicates when on SSH connection: if this prompt is set on a machine accessed by SSH it will contain static marker to the prompt. There's no point from this widget on machine which you always control directly (e.g. laptop).

## WG_SSH_ADDRESS
static dispatch
Displays server address when on SSH connection: if this prompt is used on a machine accessed by SSH it will contain the address by which server was accessed. There's no point from this widget on machine which you always control directly (e.g. laptop).

### WG_CURRENT_DIR
dynamic dispatch
Displays current working directory path with some additional processing: use custom separators between directories instead of '/' (it allows to achieve some nice-looking effects), shorten the path by replacing the middle part with '...'. If you don't need this effects, consider using 0-overhead `WG_CUSTOM` with '\\w' content instead.

### WG_JOBS_NUMBER
dynamic dispatch
Display background jobs number if any.

### WG_ERROR_CODE
dynamic dispatch
Display return code for last command if error. The error code will be displayed until you execute next command successfully.

### WG_GIT_BRANCH
dynamic dispatch
Display current git branch when your current working directory is a git repository.

### WG_GIT_MARKER
dynamic dispatch
Indicate static marker if your current working directory is a git repository.

### WG_CUSTOM
static dispatch
Any custom text (e.g. bash promptescape-chars)

