# qb-prompt  

<p align="center">
  <img src="https://user-images.githubusercontent.com/4020369/38257464-d8592036-3792-11e8-8495-a5ba7204c7e2.png"/>
</p>

## Description

**qb-prompt** is an easily-customizable bash prompt, which tries to combine good look and powerfull features with the best possible performance.  

It is visually inspired by [Powerline](https://github.com/powerline/powerline), which implements beautiful status lines and prompts for vim, tmux, bash, zsh and some other apps. **qb-prompt** aims to provide similar look and feel, but focuses on bash prompt only, which gives a freedom for the more efficient approach (more details below).  

**qb-prompt** supports several "widgets" (as I call parts of the prompt here), which can be toggled, reordered and variously configured by input configuration file:
* User marker - indicates if the current user is root or not with markers (`$` and `#`) and colors
* User name - current user's name with different colors for root and non-roots
* Current directory - prettified current directory path, shortened in the middle if too long
* Error code - indicates last return code, if non-zero
* Background jobs - prints the number of background processes, if any
* SSH marker - indicator of SSH connection
* SSH address - indicator of SSH connection with the server address
* Git marker - indicator of git repository
* Git branch - indicator of git repository with current branch
* Custom - any text or [bash prompt special character](https://www.gnu.org/software/bash/manual/bashref.html#Controlling-the-Prompt) decorated by qb-prompt. In fact, simplified alternatives for the majority of above widgets can be implemented using it

If you come up with a useful widget idea that can't be implemented by 'Custom' widget - feel free to suggest [here](https://github.com/azymohliad/qb-prompt/issues/new) 

[Video overview (youtube)](https://www.youtube.com/watch?v=7FGvnQuVvH4) (a little outdated)


## How it works
 
* User configures prompts (enabled widgets, their alignment side, position, colors, decorations, etc) in simple JSON-formatted file
* Then the python script `generate.py` uses it to generate not very human-readable but highly efficient shell script `qb-prompt.sh`
* `qb-prompt.sh` provides ready to use prompts (environment variables `PS1`, `PS2`, `PS3`, `PS4` and `PROMPT_COMMAND` depending on configuration) for bash interpreter and should be simply sourced from `bashrc` file.

Generation stage tries to statically resolve needed values and hardcode them into the final script to minimize the runtime of the final script. However it is not always possible: some values must be evaluated every time you log in to shell (like ssh address, user highlighting color), and some values must be evaluated every time the prompt is printed (like background jobs number, error code, git branch, etc). It might have noticable effect on the performance, so choose widgets thoughtfully when configuring (although I haven't noticed any lag even with full feature set enabled). You can try different configs and compare the complexity of the resulting `qb-prompt.sh`.  

This approach allows having both: convenient configuration and the best performance.


## Installation

**1. Install dependencies**  
qb-prompt uses Powerline fonts. Check out [this link](https://powerline.readthedocs.io/en/latest/installation/linux.html#fonts-installation) for installation instructions. Note, if you have an error on the 4th step (no such file or directory ~/.config/fontconfig/conf.d/) - just create it.
If you use Arch Linux simply install `powerline-fonts` package.  
Actually Powerline fonts is not a strict dependency, it's just the default config uses it. You can use any custom fonts for widget terminators, directory separators, etc. But if you want these beatiful arrowed backgrounds - you need Powerline fonts.

**2. Get qb-prompt.sh**  
**Simple way**: download `qb-prompt.sh` generated with default configuration from repository
```
wget https://raw.githubusercontent.com/azymohliad/qb-prompt/master/qb-prompt.sh
```
Note that default config doesn't include git branch and ssh address widgets.  

**Customizable way**: generate it from your own configuration
- Download or clone the repostory files
```
git clone https://github.com/azymohliad/qb-prompt.git && cd qb-prompt
```
- Define your configuration in a config file (e.g. `config.json`). You can check [sample_configs](https://github.com/azymohliad/qb-prompt/tree/master/sample_configs) as a starting point and customize them for your needs and taste. Check out [CONFIGURATION.md](https://github.com/azymohliad/qb-prompt/blob/master/CONFIGURATION.md) for more details
- Generate `qb-prompt.sh`:
```
./generate.py [your/input/config.json] [your/output/qb-prompt.sh]
```

**3. Source it from your `bashrc` file.**  
Add these lines to the end of your `~/.bashrc` (for the current user) or `/etc/bash.bashrc` (for all users):
```
# qb-prompt
. /path/to/qb-prompt.sh
```

**4. Relogin to your bash and have fun**


## Contributing

There is not much to do here. Feel free to report issues or suggest small improvements (including features, performance optimizations, coding style etc). But one of my priorities is to keep it lightweight and fast, so I might be sceptic about new features.


## License

Licensed under the [MIT](https://opensource.org/licenses/MIT) license.
