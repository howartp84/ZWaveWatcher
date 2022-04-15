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

import csv

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
		self.version = pluginVersion

		self.watchIDs = list()

		self.zedFromDev = dict()
		self.zedFromNode = dict()
		self.devFromZed = dict()
		self.devFromNode = dict()
		self.nodeFromZed = dict()
		self.nodeFromDev = dict()

		self.csvCmds = dict()
		self.csvTables = dict()
		self.csvBits = dict()

		reader = csv.DictReader(open('csvCmds.csv'))

		result = {}
		for row in reader:
			key = row.pop('key')
			result[key] = row
		#self.debugLog(result)

		self.csvCmds = result

		reader = csv.DictReader(open('csvTables.csv'))

		result = {}
		for row in reader:
			key = row.pop('key')
			result[key] = row
		#self.debugLog(result)

		self.csvTables = result

		reader = csv.DictReader(open('csvBits.csv'))

		result = {}
		for row in reader:
			key = row.pop('key')
			result[key] = row
		#self.debugLog(result)

		self.csvBits = result



	########################################
	def startup(self):
		self.debugLog(u"startup called")
		self.debugLog("Plugin version: {}".format(self.version))
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

		#self.debugLog(int(bytes[5],16))

		if (int(bytes[5],16)) in self.watchIDs:
			devID = self.zedFromNode[int(bytes[5],16)]
			classStr = indigo.devices[devID].ownerProps['zwClassCmdMapStr']
			#self.debugLog(indigo.devices[devID])

			if (endpoint == None):
				self.debugLog(u"Raw command received (Node {}): {}".format((int(bytes[5],16)),(byteListStr)))
				self.cmdDecode(cmd,classStr)
			else:
				self.debugLog(u"Raw command received (Node {} Endpoint {}): {}".format((int(bytes[5],16)),endpoint,(byteListStr)))
			#self.debugLog(u"Node ID {} (Hex {}) found in watchIDs".format((int(bytes[5],16)),(int(bytes[5],16))))  #THIS LINE DOESN'T LOOK RIGHT IF I EVER UNCOMMENT IT
		elif (int(bytes[5],16)) == 2:
			if (bytes[7] == "86") and (bytes[8] == "11"): #Version
				self.debugLog(u"Received 86 11 request.  Sending 86 12 02 04 020 07 01")
				codeStr = [0x86, 0x12, 0x02, 0x04, 0x20, 0x07, 0x01] #Controller, 4.32, 7.1
				indigo.zwave.sendRaw(node=2,cmdBytes=codeStr,sendMode=0,waitUntilAck=False)
			if (bytes[7] == "72") and (bytes[8] == "04"): #ZStick ID
				self.debugLog(u"Received 72 04 request.  Sending 72 05 01 4F 00 01 00 01")
				codeStr = [0x72, 0x05, 0x01, 0x4F, 0x00, 0x01, 0x00, 0x01]
				indigo.zwave.sendRaw(node=2,cmdBytes=codeStr,sendMode=0,waitUntilAck=False)



	def cmdDecode(self, cmd, classStr):
		byteList = cmd['bytes']			# List of the raw bytes just received.
		byteListStr = convertListToHexStr(byteList)
		bytes = byteListStr.split()
		#self.debugLog(classStr)

		cmdClass = bytes[7]
		cmdType = bytes[8]
		cmdPos = classStr.index(cmdClass)
		cmdVer = classStr[cmdPos+3:cmdPos+4] #25v1 => 1
		cmdKey = "{} {} v{}".format(cmdClass,cmdType,cmdVer)

		try:
			cmdDict = self.csvCmds[cmdKey]
		except KeyError as k:
			self.debugLog("Command class: {}v{}".format(cmdClass,cmdVer))
			self.debugLog("Command not yet decoded: {}".format(cmdKey))
			return

		cmdName = cmdDict['cmdName']

		self.debugLog("Command class: {}v{} ({})".format(cmdClass,cmdVer,cmdName))

		#self.debugLog(cmdDict)

		byteSize = cmdDict['byteSize']
		for i in range(9,int(byteSize)+9):
			val = cmdDict[str(i)]
			if "[TAB" in val:
				tblPos = val.index("[TAB")
				tblStr = "[TAB{}]".format(val[tblPos+4:tblPos+6])
				tblVal = self.csvTables[tblStr]
				#self.debugLog("tblVal => {}".format(tblVal))
				if tblVal['fixed'] == "T":
					for b in range(1,int(tblVal['size'])+1):
						#self.debugLog("{} in {}".format(bytes[i],tblVal[str(b)]))
						#self.debugLog(str(bytes[i] in tblVal[str(b)]))
						if bytes[i] in tblVal[str(b)]:
							self.debugLog(val.replace(tblStr,tblVal[str(b)]))
				else:
					self.debugLog(val.replace(tblStr,"0x{}, see table:".format(bytes[i])))
					for b in range(1,int(tblVal['size'])+1):
						self.debugLog("   {}".format(tblVal[str(b)]))
			elif "#" in val: #Decimal
				self.debugLog("{} {}".format(val.replace(" #",""),int(bytes[i],16)))
			elif "%" in val: #Percent
				self.debugLog("{} {}%".format(val.replace(" %",""),int(bytes[i],16)))
			elif "@" in val: #Both
				self.debugLog("{} 0x{} ({})".format(val.replace(" @",""),bytes[i],int(bytes[i],16)))
			else: #Hex by default
				self.debugLog("{} 0x{}".format(val,bytes[i]))




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
					self.debugLog(u"Raw command sent (Node {}): {} ({})".format(nodeId,byteListStr,cmdSuccess))
				else:
					self.debugLog(u"Raw command sent (Node {} Endpoint {}): {} ({})".format(nodeId,endpoint,byteListStr,cmdSuccess))

