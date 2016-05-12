# SublimeStorm-DPalette
This is a plugin provided by SublimeStorm.

Want install? See [Installation](https://github.com/iamstorm/SublimeStorm/)

## This pacakge has several very usefull tools for sublime text:

### 1. Another command palette(also named as storm palette)
It give you another command palette which just contain your wanted commands written in your personal config json file.
If you have lots of self customized commands that are not invoked very offen (not for edit code but for toolchaining) and you want to invoke it easily then you will need this plugin.

For the above purpose, the buildin command palette seem a good candidate for it. But when you install lot of packages, the command palette will be polluted by some commands which you don't want. And what is more, the name in the command palette is not in your control.The storm palette come into rescue for this case. It give you all control. And you can just write command binding in the json file. In this pacakage, it also provide some command for you to easily write command binding:
commands:
- storm_palette           # show the quick panel for all the bindings you writed
- mul_run                 # invoke multiple commands in a single binding
- run_shell_cmd           # run shell tool in sublime text
- eval_python_code        # directly run python code in a binding
- storm_palette_record    # prompt and input some keyword and auto record a new binding in the dynamic json binding file
- manage_snippet_base     # copy some code as snippet, and use this snippet on the fly

for the favor of the binding you will write, see the following examples:
```
{
    "assets": [
        {"key": "publish package to github",
         "command": "run_shell_cmd",  "args": {
            "questions": [{"key": "message", "title": "commit message",
                          "pattern": "^\\s*(?P<message>.+?)?\\s*$", "answer_tempate": "{{message}}",
                          "default_dict": {"message": "auto commit"}}],
            "commands": ["git add -A", "git commit -m \"{{message}}\"", "git push"],
            "run_opts": {"cwd": "${packages}"}}
        },
        
        {"key": "open package directory",
         "command": "run_shell_cmd",  "args": {
            "commands": ["cmd /c start \"\" \"${packages}\""]}
        },
        
        {"key": "git difftool", "command": "mul_run" , "args": {
                "commands" : [
                    {"command": "save"},
                    {"command": "run_shell_cmd",
                        "args":{
                            "commands": ["cmd /c git difftool \"${file}\""],
                            "run_mode": "run","win_mode": "hide"
                        }, "context": "window"
                    },
            ]}
        },
        
        {"key": "record global file", "command": "storm_palette_record",  "args": {
            "questions": [{"key": "palkey"}],
            "content": {
                "key": "{{palkey}}",
                "command": "eval_python_code",
                "args": {
                    "code": "sublime.active_window().open_file(\"${file!unixpath}\")",
                    "show_result": "error"
                }
            }}
        },
        {"key": "record project file", "command": "storm_palette_record",  "args": {
            "questions": [{"key": "palkey"}],
            "belong_to_project": true,
            "content": {
                "key": "{{palkey}}",
                "command": "eval_python_code",
                "args": {
                    "code": "sublime.active_window().open_file(\"${file!unixpath}\")",
                    "show_result": "error"
                }
            }}
        },
    ]
}
```

see the file:`storm_palette.sublime-settings` and edit the `palkey_path` key to locate your private binding files
the binding files is a json file with name `default.stormpal.key` and with the content as above

### 2. A very functional palette which use to record tips for future:
- search_ref_palette      # show the quick panel for all the tip (markdown format) you writed
you can add a binding to be invoke by storm palette:
```
{
    "assets": [
        {"key": "search reference palette", "command": "search_ref_palette"}
    ]
}
```

see the file:`search_ref_palette.sublime-settings` and edit the `palkey_path` key to locate your private markdown tip files,
the palette will parse the markdown file and show the header section for you to select, and it will preview the content in a seperate view(auto created and destroyed)

### 3. A clipboard palette
- clipboard_palette     # show quick panel for your regesited texts
There are some times you wanted to keep some temporary text which is from selection or from clipboard. you can use this command to register text with key. And afterward, you can use this key to fetch the text
