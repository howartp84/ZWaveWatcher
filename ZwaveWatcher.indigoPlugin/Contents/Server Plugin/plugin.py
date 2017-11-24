#! /usr/bin/env python
# -*- coding: utf-8 -*-
####################
# Copyright (c) 2016, Perceptive Automation, LLC. All rights reserved.
# http://www.indigodomo.com

#Thanks to Krisstian for teaching me how to join() and use xrange() in one-liner commands!

import indigo

import os
import sys

import fnmatch

# Note the "indigo" module is automatically imported and made available inside
# our global name space by the host process.

########################################
# Tiny function to convert a list of integers (bytes in this case) to a
# hexidecimal string for pretty logging.
def convertListToHexStr(byteList):
	return ' '.join(["%02X" % byte for byte in byteList])

def convertListToStr(byteList):
	return ' '.join(["%02X" % byte for byte in byteList])

################################################################################
class Plugin(indigo.PluginBase):
	########################################
	def __init__(self, pluginId, pluginDisplayName, pluginVersion, pluginPrefs):
		super(Plugin, self).__init__(pluginId, pluginDisplayName, pluginVersion, pluginPrefs)
		self.debug = True;

		self.watchIDs = list()

		self.zedFromDev = dict()
		self.zedFromNode = dict()
		self.devFromZed = dict()
		self.devFromNode = dict()
		self.nodeFromZed = dict()
		self.nodeFromDev = dict()

	########################################
	def startup(self):
		self.debugLog(u"startup called")
		indigo.zwave.subscribeToIncoming()
		indigo.zwave.subscribeToOutgoing()

	def shutdown(self):
		self.debugLog(u"shutdown called")

	def deviceStartComm(self, dev):
		dev.stateListOrDisplayStateIdChanged()
		if (dev.deviceTypeId == "zwatch"):
			devID = dev.id																							#devID is the Indigo ID of my dummy device
			zedID = dev.ownerProps['deviceId']													#zedID is the Indigo ID of the actual ZWave device
			nodeID = indigo.devices[int(zedID)].ownerProps['address']		#nodeID is the ZWave Node ID

			self.zedFromDev[int(devID)] = int(zedID)
			self.zedFromNode[int(nodeID)] = int(zedID)
			self.devFromZed[int(zedID)] = int(devID)
			self.devFromNode[int(nodeID)] = int(devID)
			self.nodeFromZed[int(zedID)] = int(nodeID)
			self.nodeFromDev[int(devID)] = int(nodeID)

			self.watchIDs.append(nodeID)

	def deviceStopComm(self, dev):
		if (dev.deviceTypeId == "zwatch"):
			devID = dev.id
			zedID = dev.ownerProps['deviceId']
			nodeID = indigo.devices[int(zedID)].ownerProps['address']

			self.zedFromDev.pop(int(devID),None)
			self.zedFromNode.pop(int(nodeID),None)
			self.devFromZed.pop(int(zedID),None)
			self.devFromNode.pop(int(nodeID),None)
			self.nodeFromZed.pop(int(zedID),None)
			self.nodeFromDev.pop(int(devID),None)

			self.watchIDs.remove(nodeID)



########################################
	def zwaveCommandReceived(self, cmd):
		byteList = cmd['bytes']			# List of the raw bytes just received.
		byteListStr = convertListToHexStr(byteList)
		nodeId = cmd['nodeId']			# Can be None!
		endpoint = cmd['endpoint']		# Often will be None!

		bytes = byteListStr.split()
		#nodeId = int(bytes[5],16)

		if (int(bytes[5],16)) in self.watchIDs:
			if (endpoint == None):
				self.debugLog(u"Raw command received (Node %s): %s" % ((int(bytes[5],16)),(byteListStr)))
			else:
				self.debugLog(u"Raw command received (Node %s Endpoint %s): %s" % ((int(bytes[5],16)),endpoint,(byteListStr)))
			#self.debugLog(u"Node ID %s (Hex %s) found in watchIDs" % ((int(bytes[5],16)),(int(bytes[5],16))))

########################################
	def zwaveCommandSent(self, cmd):
		byteList = cmd['bytes']         # List of the raw bytes just sent.
		byteListStr = convertListToHexStr(byteList)    # this method is defined in the example SDK plugin
		timeDelta = cmd['timeDelta']    # The time duration it took to receive an Z-Wave ACK for the command.
		cmdSuccess = cmd['cmdSuccess']  # True if an ACK was received (or no ACK expected), false if NAK.
		nodeId = cmd['nodeId']          # Can be None!
		endpoint = cmd['endpoint']      # Often will be None!

		bytes = byteListStr.split()

		bytes = byteListStr.split()
		#nodeId = int(bytes[5],16)

		if nodeId:
			if int(nodeId) in self.watchIDs:
				if (endpoint == None):
					self.debugLog(u"Raw command sent (Node %s): %s (%s)" % (nodeId,byteListStr,cmdSuccess))
				else:
					self.debugLog(u"Raw command sent (Node %s Endpoint %s): %s (%s)" % (nodeId,endpoint,byteListStr,cmdSuccess))

