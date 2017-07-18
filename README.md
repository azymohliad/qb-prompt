# qb-prompt
**Q**uick and **B**eautiful **prompt** for bash.  

It is inspired by [Powerline](https://github.com/powerline/powerline), which is feature rich project written in Python. I happily used it for some time, but got annoyed by it's low performance (at least on my old machine).   
**qb-prompt** aims to provide similar look and feel, at the same time remaining as simple and lightweight as possible. It is just a tiny shell-script which you can even simply paste into your `.bashrc` file. Currently it works only with bash. It doesn't have vim, tmux statuslines, git integration, etc. If you look for something more powerfull, check out [Powerline](https://github.com/powerline/powerline).

![screenshot from 2017-07-18 18-11-44](https://user-images.githubusercontent.com/4020369/28313033-d6102df0-6be7-11e7-95df-53f1735812e3.png)

As it already looks nice enough to me, performance is the next top priority. I plan to try adding few more features (return code indication, display working jobs number, display current git branch, etc), but if they will notably decrease performance, most probably I won't add them.

## Installation
**1. Download the script**
E.g. into your home dir:
```
wget -O ~/.qb-prompt.sh https://raw.githubusercontent.com/azymohliad/qb-prompt/master/qb-prompt.sh
```

**2. Source it from your `~/.bashrc` file.**
Add these lines to the end of it:
```
# qb-prompt
if [ "${TERM}" == "xterm-256color" ]; then
    . ~/.qb-prompt.sh
fi
```
I added this if-condition to enable it only for terminals with 256-colors support. 
You may alternatively want to do it in global `/etc/bash.bashrc` file to make it available for all users. Note that you would need to specify full path to the script. Also in this case it would be better to put `qb-prompt.sh` to some user-independent place.

If you have any question or comment, which in your opinion doesn't worth raising issue, you ask it [here](https://github.com/azymohliad/qb-prompt/issues/1).
