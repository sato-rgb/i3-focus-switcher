# i3-focus-switcher

##How to use
Add the following lines to your ``.i3/config``:

```
# Switch splits
set $spl_next "~/.config/i3/i3-focus-changer.py n s"
set $spl_prev "~/.config/i3/i3-focus-changer.py p s"
bindsym $mod+j exec $spl_prev
bindsym $mod+k exec $spl_next

# Switch tabs
set $tab_next "~/.config/i3/i3-focus-changer.py n t"
set $tab_prev "~/.config/i3/i3-focus-changer.py p t"
bindsym $mod+h exec $tab_prev
bindsym $mod+l exec $tab_next
```

this script does not support
- multi monitor
- jump to other workspace
- stacking
