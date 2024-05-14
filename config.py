# Copyright (c) 2010 Aldo Cortesi
# Copyright (c) 2010, 2014 dequis
# Copyright (c) 2012 Randall Ma
# Copyright (c) 2012-2014 Tycho Andersen
# Copyright (c) 2012 Craig Barnes
# Copyright (c) 2013 horsik
# Copyright (c) 2013 Tao Sauvage
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from libqtile import bar, layout, qtile
from qtile_extras import widget
from libqtile.config import Click, Drag, Group, Key, Match, Screen
from libqtile.lazy import lazy
from libqtile.log_utils import logger

from libqtile import hook
from libqtile.utils import send_notification
from qtile_extras.widget.decorations import RectDecoration, PowerLineDecoration


mod = "mod4"
terminal = "alacritty"
browser = "firefox"
quickTerminal = "alacritty --title quick-terminal"
lowBrightness = False


def toggleBrightness(qtile):
    global state
    if (state is False):
        qtile.cmd_spawn("xrandr --output HDMI-1 --brightness 0.5")
        qtile.cmd_spawn("xrandr --output DP-1 --brightness 0.5")
        state = True
    else:
        qtile.cmd_spawn("xrandr --output HDMI-1 --brightness 1")
        qtile.cmd_spawn("xrandr --output DP-1 --brightness 1")
        state = False



keys = [
    # A list of available commands that can be bound to keys can be found
    # at https://docs.qtile.org/en/latest/manual/config/lazy.html
    # Switch between windows
    Key([mod], "h", lazy.layout.left(), desc="Move focus to left"),
    Key([mod], "l", lazy.layout.right(), desc="Move focus to right"),
    Key([mod], "j", lazy.layout.down(), desc="Move focus down"),
    Key([mod], "k", lazy.layout.up(), desc="Move focus up"),
    Key(["mod1"], "Tab", lazy.layout.next(), desc="Move window focus to other window"),
    # Move windows between left/right columns or move up/down in current stack.
    # Moving out of range in Columns layout will create new columnr
    Key([mod, "shift"], "h", lazy.layout.shuffle_left(), desc="Move window to the left"),
    Key([mod, "shift"], "l", lazy.layout.shuffle_right(), desc="Move window to the right"),
    Key([mod, "shift"], "j", lazy.layout.shuffle_down(), desc="Move window down"),
    Key([mod, "shift"], "k", lazy.layout.shuffle_up(), desc="Move window up"),

    # Grow windows. If current window is on the edge of screen and direction
    # will be to screen edge - window would shrink.
    Key([mod, "control"], "h", lazy.layout.grow_left(), desc="Grow window to the left"),
    Key([mod, "control"], "l", lazy.layout.grow_right(), desc="Grow window to the right"),
    Key([mod, "control"], "j", lazy.layout.grow_down(), desc="Grow window down"),
    Key([mod, "control"], "k", lazy.layout.grow_up(), desc="Grow window up"),
    Key([mod], "n", lazy.window.toggle_minimize(), desc="Grow window up"),
    Key([mod], "m", lazy.group.unminimize_all(), desc="Grow window up"),

    # go to the next screen
    Key(["control"], "Tab", lazy.next_screen(), desc="Next monitor"),
    # Toggle between split and unsplit sides of stack.
    # Split = all windows displayed
    # Unsplit = 1 window displayed, like Max layout, but still with
    # multiple stack panes
    Key(
        [mod, "shift"],
        "Return",
        lazy.layout.toggle_split(),
        desc="Toggle between split and unsplit sides of stack",
    ),
    Key([mod], "Return", lazy.spawn(terminal), desc="Launch terminal"),
    Key([mod, "shift"], "Return", lazy.spawn(quickTerminal), desc="Launch terminal"),
    Key(["control"], "f", lazy.spawn(browser), desc="launch firefox"),
    # screenshot controls
    Key([], "Print", lazy.spawn("scrot -s pictures/screenshot/capture.png"), desc="takes a screenshot"),
    # Volume controls
    Key([], "XF86AudioRaiseVolume", lazy.spawn("amixer set Master 5%+"), desc="Increase volumen"),
    Key([], "XF86AudioLowerVolume", lazy.spawn("amixer set Master 5%-"), desc="Decrease volumen"),
    # Toggle between different layouts as defined below
    Key([mod], "space", lazy.next_layout(), desc="Toggle between layouts"),
    Key(["mod1"], "w", lazy.window.kill(), desc="Kill focused window"),
    Key(
        [mod],
        "f",
        lazy.window.toggle_fullscreen(),
        desc="Toggle fullscreen on the focused window",
    ),
    Key([mod], "t", lazy.window.toggle_floating(), desc="Toggle floating on the focused window"),
    Key([mod, "control"], "r", lazy.reload_config(), desc="Reload the config"),
    Key([mod, "control"], "q", lazy.shutdown(), desc="Shutdown Qtile"),
    Key([mod], "r", lazy.spawncmd(), desc="Spawn a command using a prompt widget"),
    # screen shorcuts
    Key([mod], "p",
        lazy.function(toggleBrightness),
        desc="toggle brightness low/high"),
]

# Add key bindings to switch VTs in Wayland.
# We can't check qtile.core.name in default config as it is loaded before qtile is started
# We therefore defer the check until the key binding is run by using .when(func=...)
for vt in range(1, 8):
    keys.append(
        Key(
            ["control", "mod1"],
            f"f{vt}",
            lazy.core.change_vt(vt).when(func=lambda: qtile.core.name == "wayland"),
            desc=f"Switch to VT{vt}",
        )
    )


groups = [Group(i) for i in "123456789"]
# groups = [Group("󰈹"), Group(""), Group(""), Group("󰈸"), Group("󰊗"), ]

for i in groups:
    keys.extend(
        [
            # mod1 + group number = switch to group
            Key(
                [mod],
                i.name,
                lazy.group[i.name].toscreen(),
                desc="Switch to group {}".format(i.name),
            ),
            # mod1 + shift + group number = switch to & move focused window to group
            Key(
                [mod, "shift"],
                i.name,
                lazy.window.togroup(i.name),
                desc="Switch to & move focused window to group {}".format(i.name),
            ),
            # Or, use below if you prefer not to switch to that group.
            # # mod1 + shift + group number = move focused window to group
            # Key([mod, "shift"], i.name, lazy.window.togroup(i.name),
            #     desc="move focused window to group {}".format(i.name)),
        ]
    )

layouts = [
    layout.Columns(
        border_focus="#fbf1c7",
        border_normal="#665c54",
        border_width=2,
        border_on_single=True,
        margin=15)
    # layout.Tile(),
    # layout.Max(),
    # Try more layouts by unleashing below layouts.
    # layout.Stack(num_stacks=2),
    # layout.Bsp(),
    # layout.Matrix(),
    # layout.MonadTall(),
    # layout.MonadWide(),
    # layout.RatioTile(),
    # layout.TreeTab(),
    # layout.VerticalTile(),
    # layout.Zoomy(),
]

widget_defaults = dict(
    font="FiraCode Nerd Font Propo",
    fontsize=13,
)
extension_defaults = widget_defaults.copy()

groupDecor = {
    "decorations": [
        RectDecoration(colour="#282828", radius=15, filled=True, padding_y=2, line_colour="#1d2021", line_width=1.5)
    ],
    "padding": 5,
}
promptDecor = {
    "decorations": [
        RectDecoration(colour="#fe8019", radius=15, filled=True, padding_y=2, line_colour="#d65d0e", line_width=1.5)
    ],
    "padding": 15,
}
archDecor = {
    "decorations": [
        RectDecoration(colour="#282828", radius=15, filled=True, padding_y=2, line_colour="#1d2021", line_width=1.5)
    ],
    "padding": 20,
}

clockDecor = {
    "decorations": [
        RectDecoration(colour="#fabd2f", radius=15, filled=True, padding_y=2, line_colour="#d79921", line_width=1.5)
    ],
    "padding": 20,
}
nameDecor = {
    "decorations": [
        RectDecoration(colour="#282828", radius=15, filled=True, padding_y=2, line_colour="#1d2021", line_width=1.5)
    ],
    "padding": 5,
}


screens = [
    Screen(
        top=bar.Bar(
            [
                # widget.CurrentLayout(),
                widget.TextBox("", fontsize=20, **archDecor),
                widget.Spacer(length=10),
                widget.GroupBox(
                    highlight_method="text",
                    this_current_screen_border="fe8019",
                    active="FFF",
                    fontsize=15,
                    margin_x=5,
                    **groupDecor
                    ),
                widget.Spacer(length=50),
                # widget.TaskList(),
                widget.Prompt(fontsize=15, font="semibold", foreground="fff", **promptDecor),
                widget.Spacer(length=10),
                widget.WindowName(fmt="  <i>{}</i>", max_chars=90, **nameDecor),
                widget.Spacer(length=50),
                # widget.Memory(padding=10, font="FiraCode Nerd Font Propo", format="\uf013 <i>{MemUsed: .0f}{mm}</i>"),
                # widget.CPU(padding=15, font="sans",  format="\uf26c   <i>{freq_current}Ghz {load_percent}%</i>"),
                widget.Clock(format="\uf073  %d . %m . %Y  \uf4ab  %I:%M %p",  font="sans medium", fontsize=14, foreground="1d2021", **clockDecor),
            ],
            35,
            margin = [ 5, 20, 0, 20],
            background="#00000000"
            #background="504945",

        ),
        # You can uncomment this variable if you see that on X11 floating resize/moving is laggy
        # By default we handle these events delayed to already improve performance, however your system might still be struggling
        # This variable is set to None (no cap) by default, but you can set it to 60 to indicate that you limit it to 60 events per second
        # x11_drag_polling_rate = 60,
    )
]

# Drag floating layouts.
mouse = [
    Drag([mod], "Button1", lazy.window.set_position_floating(), start=lazy.window.get_position()),
    Drag([mod], "Button3", lazy.window.set_size_floating(), start=lazy.window.get_size()),
    Click([mod], "Button2", lazy.window.bring_to_front()),
]

dgroups_key_binder = None
dgroups_app_rules = []  # type: list
follow_mouse_focus = True
bring_front_click = False
floats_kept_above = True
cursor_warp = False
floating_layout = layout.Floating(
    float_rules=[
        # Run the utility of `xprop` to see the wm class and name of an X client.
        *layout.Floating.default_float_rules,
        Match(wm_class="confirmreset"),  # gitk
        Match(wm_class="makebranch"),  # gitk
        Match(wm_class="maketag"),  # gitk
        Match(wm_class="ssh-askpass"),  # ssh-askpass
        Match(title="branchdialog"),  # gitk
        Match(title="pinentry"),  # GPG key password entry
        Match(title="quick-terminal"),  # GPG key password entry
    ]
)
auto_fullscreen = True
focus_on_window_activation = "smart"
reconfigure_screens = True

# If things like steam games want to auto-minimize themselves when losing
# focus, should we respect this or not?
auto_minimize = True

# When using the Wayland backend, this can be used to configure input devices.
wl_input_rules = None

# XXX: Gasp! We're lying here. In fact, nobody really uses or cares about this
# string besides java UI toolkits; you can see several discussions on the
# mailing lists, GitHub issues, and other WM documentation that suggest setting
# this string if your java app doesn't work correctly. We may as well just lie
# and say that we're a working one by default.
#
# We choose LG3D to maximize irony: it is a 3D non-reparenting WM written in
# java that happens to be on java's whitelist.
wmname = "LG3D"


# Defining hooks

# send_notification("qtile", "Focus swicht...")

#@hook.subscribe.group_window_add
#def group_window_add(group, window):
    # if window.name == "quick-terminal":
        # window.enable_floating()
