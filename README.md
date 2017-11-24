#ZWave Watcher

This is an Indigo 7 plugin that I've written to aid debugging of new ZWave devices on the market. When dealing with ZWave command queries, the builtin method for debugging them is to turn on ZWave Debugging (Interfaces > .ZWave > Configure > Show debugging... but this fills the logs with tonnes of ZWave traffic for every node in your system.

This plugin allows you to choose which node(s) you want to watch/debug, then only logs the incoming and outgoing ZWave commands for those specific node(s). 

This should help myself and Matt (Support) to help you with your question, but it will also help you start to do your own digging.