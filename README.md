This is modified from the lsp-example code at https://code.visualstudio.com/api/language-extensions/language-server-extension-guide

# VSCode Rat Extension

This is the vscode extension for the [rat](https://github.com/bbbales2/regressions)
programming language.

I'm not quite sure how to install this extension in vscode, but to debug it use vscode and there should be a "Launch Client" debug configuration in .vscode/launch.json that will launch a second
vscode client with the extension active.

To use the VSCode Rat Extension, the `rat-language-server` command must be in the PATH
variable of the client launched with this extension. The easiest way to guarantee this is true
is by making sure `rat-language-server` is in the PATH of the vscode instance from which
the second test vscode client is active.

To make sure `rat-language-server` is in the PATH, make sure that you can run
`rat-language-server` from the command line that you use to launch vscode.
