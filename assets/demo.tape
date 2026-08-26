# Terminal demo for the README, rendered with VHS: https://github.com/charmbracelet/vhs
#
#   vhs assets/demo.tape        # run from the repository root
#
# A script rather than a screen recording, so the demo can be re-rendered when
# the CLI changes instead of quietly going out of date the way a video would.
#
# Output goes to output/, which is gitignored, so rendering leaves no residue.
# Do not set a shell here: VHS on Windows renders nothing with `Set Shell bash`.

Output assets/demo.gif

Set FontSize 15
Set Width 1180
Set Height 940
Set Theme "Catppuccin Mocha"
Set TypingSpeed 40ms
Set Padding 22
Set BorderRadius 8

Sleep 1s

# One command: a full retail star schema in Spanish, two formats, FK-verified.
Type "cug generate -n 50000 -f parquet,csv -l es -o output/demo --strict"
Sleep 400ms
Enter
Sleep 15s

# Localization depth is computed from the data, never claimed by hand.
Type "cug info"
Sleep 400ms
Enter
Sleep 7s
