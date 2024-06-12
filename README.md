# live-node-monitor

WORK IN PROGRESS

This tool is currently still being designed and actively worked on. Use at your own risk!

## What problems does this tool solve?

Usually, machine monitoring focusses on time-series data (e.g. metrics) and logging data (e.g. logs, documents).
Logging data is very useful in order to debug issues in the machine's operating system or in an application.
However, a machine can generate many logs. Sometimes it is not feasible to store all generated logs of every machine in a remote backend. A large percentage of this data is not needed and wastes storage resources.
In addition, some interesting events are not always logged, e.g. OoM events.
Some of these events can be extracted from the commandline, e.g. via a specific shell command.

### Features

- Save storage resources with an event based log monitoring approach: Only watch for specific events and upload only whats necessary.
- Customize and transform the uploaded data: Use custom regular expressions with named groups, to parse log lines and store the data with customized keys.
- Generate anything: Use custom shell commands on the machine to extract exactly the data you want. Extract data periodicially to watch for certain changes, or even design custom health-checks for your use case.
- Easy to use: No need for building custom data extraction logic. If it can be logged to stdout, you can upload it.

## Components

### continuous monitors

- log_monitor: continuously watches logs, parses them and uploads interesting data to a remote backend.

### periodic monitors

- command_monitor: Execute a shell command and upload its output to a remote backend. You can even repeat this command periodically.
