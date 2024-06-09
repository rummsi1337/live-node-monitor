# live-node-monitor

WORK IN PROGRESS

This tool is currently still being designed and actively worked on. Use at your own risk!

## What problems does this tool solve?

Usually, machine monitoring focusses on time-series data (e.g. promethus) and logging data (e.g. loki).
Logging data is very useful, in order to debug issues in the machine's operating system or in an application.
However, a machine can generate many logs, usually it is not feasible to store all logs of every machine in a remote backend. 99% of this data is usually not needed and wastes storage resources.
In addition, some interesting events are not logged reliably, e.g. OoM events, or available disk space.
Some events on the machine are usually not directly logged and need to be extracted on the commandline, e.g. via a specific shell command.

### Features

- Save resources with event based log monitoring: Only watch for specific events and upload only whats necessary
- Customize uploaded data: Use custom regular expressions with named groups, to parse log lines and store the data with customized keys
- Generate anything: Use custom shell commands on the node, to extract exactly the data you want. Extract data periodicially to watch for changes, or even design custom health-checks
- Easy to use: No need for building custom data extraction logic into your application. If it can be logged, you can upload it

## Components

### continuous monitors

- log_monitor: continuously watches logs, parses them and uploads interesting data to a remote backend

### periodic monitors

- command_monitor: Execute any shell command and upload its output to a remote backend. You can even repeat this command periodically
