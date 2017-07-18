# qb-prompt

**Q**uick and **B**eautiful **prompt** for bash.  

## Description

It is inspired by [Powerline](https://github.com/powerline/powerline), which is feature rich project written in Python. I happily used it for some time, but got annoyed by it's low performance (big initial loading time, around 1 sec for me).   
**qb-prompt** aims to provide similar look and feel, at the same time remaining as simple and lightweight as possible. It is just a tiny shell-script which you can simply paste into your `.bashrc` file.
![screenshot from 2017-07-18 18-11-44](https://user-images.githubusercontent.com/4020369/28313033-d6102df0-6be7-11e7-95df-53f1735812e3.png)

As it already looks nice enough to me, keeping it fast is the next top priority. I plan to experiment with few more features (error code indication, display working jobs number, git integration, etc), but if they will notably decrease performance, most probably I won't add them.

## Installation

**1. Install dependencies**  
qb-prompt uses Powerline fonts. Check out [this link](https://powerline.readthedocs.io/en/latest/installation/linux.html#fonts-installation) for installation instructions. Note, if you have error on 4th step (no such file or directory ~/.config/fontconfig/conf.d/) just create it.
If you use Arch Linux simply install `powerline-fonts` package.

**2. Download the script**  
E.g. into your home dir:
```
wget -O ~/.qb-prompt.sh https://raw.githubusercontent.com/azymohliad/qb-prompt/master/qb-prompt.sh
```

**3. Source it from your `~/.bashrc` file.**  
Add these lines to the end of it:
```
# qb-prompt
if [ "${TERM}" == "xterm-256color" ]; then
    . ~/.qb-prompt.sh
fi
```
You may alternatively want to do it in global `/etc/bash.bashrc` file to make it available for all users. Note that you would need to specify full path to the script. Also in this case it would be better to put `qb-prompt.sh` to some user-independent place.

If you have any question or comment, which in your opinion doesn't worth raising issue, you can ask it [here](https://github.com/azymohliad/qb-prompt/issues/1). Also feel free to raise new issues.
