#ZWave Sensor Logger for Indigo Home Automation
#Introducing the ZWave Sensor Logger plugin

This is an Indigo 7 plugin that I've written to handle logging of sensor values for power strips with multiple sockets or temperature modules with multiple sensors that aren't yet supported or handled correctly in core Indigo due to the way manufacturers have implemented them.

The plugin supports up to 8 sockets per power device and up to 5 temperature sensors per temperature device. 

Current Features

Provides a "ZWave Power Logger" device type which you point at any one of your ZWave power strip devices (doesn't matter which one)
Provides a "ZWave Temperature Logger" device type which you point at any one of your ZWave temperature devices (doesn't matter which one)
Provides states for 8 power readings or 5 temperature readings per deviceProvides actions to request updated values from the module (if supported by the module - Greenwave nodes are weird)

Installation notes
This plugin creates a 'dummy' device type called Z-Wave Sensor Logger > ZWave Power Logger or > ZWave Temperature Logger.  You should create a dummy device to represent each power strip or temperature module you are logging.  The 'edit device' dialog box will display a list of all ZWave devices on your network - just pick the one you want to log and hit OK.  The plugin also provides actions called Z-Wave Sensor Logger Action > Request Power Levels and > Request Temperatures, plus >Reset power levels should you want to zero your levels. (Note this doesn't reset them in the module itself, only in your logger device)Coming soonProvide kWh energy valuesSupport °C or °F

Planned for later

Support for specific devices

Known issues
None

Those who have seen me around the forums will know I usually participate in the forums at least daily if not several times; however please be aware this is usually from my iPhone when I'm away from my desk.  I will endeavour to support this plugin as quickly as possible, but (as with everyone) I have busy periods of the year when I'm simply not at my desk long enough to do all I'd like to, including fixing or updating plugin code, even if you see me actively responding to other threads. 

Enjoy!

Peter
