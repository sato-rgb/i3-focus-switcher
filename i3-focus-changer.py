#!/usr/bin/env python3

"""
i3-focus-changer.py --

Add the following lines to your ``.i3/config``:

Switch splits ```
    set $spl_next "~/.config/i3/i3-focus-changer.py n s"
    set $spl_prev "~/.config/i3/i3-focus-changer.py p s"

    bindsym $mod+j exec $spl_prev
    bindsym $mod+k exec $spl_next
```

Switch tabs ```
    set $tab_next "~/.config/i3/i3-focus-changer.py n t"
    set $tab_prev "~/.config/i3/i3-focus-changer.py p t"

    bindsym $mod+h exec $tab_prev
    bindsym $mod+l exec $tab_next
```


"""

import subprocess
import json

ignore_name = ['__i3']
ignore_type = ['dockarea']

#LIBRARY

class Node:
    def __init__(self):
        self.parent = None
        self.children = []
        self.layout = None
        self.type = None
        self.window_id = None
        self.id = None
        self.focuses = []
        #workspace name
        self.wsname = None

    #window node only
    def is_displayd(self):
        if self.window_id == None:
            return False
        node = self
        while(True):
            if node.type == 'workspace':
                return True
            if node.parent.layout == 'splith' or node.parent.layout == 'splitv':
                node = node.parent
                continue
            if node.parent.layout == 'tabbed' or node.parent.layout == 'stacked':
                if node.parent.focuses[0] == node.id:
                    node = node.parent
                    continue
            return False

    def get_bros(self):
        ret = []
        for bro in self.parent.children:
            ret.append(bro)
        return ret

def filter_node_flat(fn,node,buf=[]):
    if fn(node):
        buf.append(node)
    for child in node.children:
        filter_node_flat(fn,child,buf)
    return buf

def filter_node_tree(fn,node,buf=[]):
    if fn(node):
        buf.append(node)
    for child in node.children:
        child_buf = []
        buf.append(child_buf)
        filter_node_tree(fn,child,child_buf)
    return buf

def emit_change_focus(window_id):
    subprocess.check_call(['i3-msg', '[id="%d"] focus' % (window_id)])

#LIBRARY END

#MAIN

#TODO:change argument order
def parse_tree_rec(node,parent,windows,wsname = None):
    if node['name'] in ignore_name:
        return
    if node['type'] in ignore_type:
        return
    if node['type'] == 'workspace':
        wsname = node['name']

    foo = Node()
    foo.parent = parent
    foo.layout = node['layout']
    foo.type = node['type']
    foo.window_id = node['window']
    foo.id = node['id']
    foo.focuses = node['focus']
    foo.wsname = wsname
    parent.children.append(foo)

    if node['focused']:
        global CUR_FOCUSED
        CUR_FOCUSED = foo
    if node['window'] is not None:
        windows.append(foo)
    if 'nodes' in node and len(node['nodes']):
        for child in node['nodes']:
            parse_tree_rec(child,foo,windows,wsname)

def parse_tree(tree):
    foo = Node()
    windows = []
    parse_tree_rec(tree,foo,windows)
    return (foo.children[0],windows)
    

def get_next_window(windows,reverse_mode=False):
    if reverse_mode:
        windows.reverse()
    #get index of current focus 
    cf = 0
    for i,n in enumerate(windows):
        if n == CUR_FOCUSED:
            cf = i
            break
    if cf == len(windows) - 1:
        return windows[0]
    else:
        return windows[cf+1]

def switch_to_next_displayed(windows,reverse_mode=False):
    #workspace windows
    ws_wins = list(filter(lambda n : n.wsname == CUR_FOCUSED.wsname and n.is_displayd(),windows))
    #displayed nodes
    #displayed_nodes = list(filter(lambda n : n.is_displayd(),windows))
    if reverse_mode:
        terget = get_next_window(ws_wins,reverse_mode=True)
    else:
        terget = get_next_window(ws_wins)
    emit_change_focus(terget.window_id)
    #print('n',terget.window_id)
    #print('p',rterget.window_id)
    #print('c',CUR_FOCUSED.window_id)

def switch_to_next_tab(windows,reverse_mode=False):
    print(windows)
    if CUR_FOCUSED.parent.layout == 'tabbed':
        ws_tabs = list(filter(lambda n : n.parent == CUR_FOCUSED.parent,windows))
        if reverse_mode:
            terget = get_next_window(ws_tabs,reverse_mode=True)
        else:
            terget = get_next_window(ws_tabs)
    emit_change_focus(terget.window_id)


def main(argv=None):
    output = subprocess.check_output(['i3-msg', '-t', 'get_tree'])
    tree = json.loads(output)

    (root,windows)= parse_tree(tree)

    
    argv_len = len(argv)
    reverse_mode = False
    current_workspace_only = True
    if argv_len >= 2:
        cmd = argv[1].lower()
        if cmd[0] == 'n':
            reverse_mode = False
        elif cmd[0] == 'p':
            reverse_mode = True
        else:
            raise ValueError('specify [n]ext or [p]rev')
    if argv_len >= 3:
        cmd = argv[2].lower()
        if cmd[0] == 's':
            switch_to_next_displayed(windows,reverse_mode)
        elif cmd[0] == 't':
            switch_to_next_tab(CUR_FOCUSED.get_bros(),reverse_mode)
        else:
            raise ValueError('specify mode:[s]plit or [t]ab')

if __name__ == '__main__':
    import sys
    sys.exit(main(argv=sys.argv))
