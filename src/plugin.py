# for localized messages
from . import _

from Plugins.Plugin import PluginDescriptor
from Components.config import config, ConfigBoolean
from Components.Harddisk import harddiskmanager
from BackupManager import BackupManagerautostart
from ImageManager import ImageManagerautostart
from SwapManager import SwapAutostart
from SoftcamManager import SoftcamAutostart
from IPKInstaller import IpkgInstaller
from os import path, listdir

def checkConfigBackup():
	try:
		devices = [ (r.description, r.mountpoint) for r in harddiskmanager.getMountedPartitions(onlyhotplug = False)]
		list = []
		images = ""
		for x in devices:
			if x[1] == '/':
				devices.remove(x)
		if len(devices):
			for x in devices:
				if path.exists(path.join(x[1],'backup')):
					images = listdir(path.join(x[1],'backup'))
				if len(images):
					for fil in images:
						if fil.endswith('.tar.gz'):
							dir = path.join(x[1],'backup')
							list.append((path.join(dir,fil),path.join(x[1],fil)))
		if len(list):
			return True
		else:
			return None
	except IOError, e:
		print "unable to use device (%s)..." % str(e)
		return None

if checkConfigBackup() is None:
	backupAvailable = 0
else:
	backupAvailable = 1

def VIXMenu(session):
	import ui
	return ui.VIXMenu(session)

def UpgradeMain(session, **kwargs):
	session.open(VIXMenu)

def startSetup(menuid):
	if menuid != "setup":
		return [ ]
	return [(_("ViX"), UpgradeMain, "vix_menu", 1010)]

config.misc.restorewizardrun = ConfigBoolean(default = False)
def RestoreWizard(*args, **kwargs):
	from RestoreWizard import RestoreWizard
	return RestoreWizard(*args, **kwargs)

def SoftcamManager(session):
	from SoftcamManager import VIXSoftcamManager
	return VIXSoftcamManager(session)

def SoftcamMenu(session, **kwargs):
	session.open(SoftcamManager)

def SoftcamSetup(menuid):
	if menuid == "cam":
		return [(_("Softcam Manager"), SoftcamMenu, "softcamsetup", 1005)]
	return []

def filescan_open(list, session, **kwargs):
	filelist = [x.path for x in list]
	session.open(IpkgInstaller, filelist) # list

def filescan(**kwargs):
	print 'PPPPPPPPPPPP'
	from Components.Scanner import Scanner, ScanPath
	return \
		Scanner(mimetypes = ["application/x-debian-package"],
			paths_to_scan =
				[
					ScanPath(path = "ipk", with_subdirs = True),
					ScanPath(path = "", with_subdirs = False),
				],
			name = "Ipkg",
			description = _("Install extensions."),
			openfnc = filescan_open, )

def Plugins(path, **kwargs):
	plist = [PluginDescriptor(where=PluginDescriptor.WHERE_MENU, needsRestart = False, fnc=startSetup)]
	plist.append(PluginDescriptor(name=_("ViX"), where=PluginDescriptor.WHERE_EXTENSIONSMENU, fnc=UpgradeMain))
	plist.append(PluginDescriptor(where=PluginDescriptor.WHERE_MENU, fnc=SoftcamSetup))
	plist.append(PluginDescriptor(name=_("Softcam Manager"), where=PluginDescriptor.WHERE_EXTENSIONSMENU, fnc=SoftcamMenu))
	plist.append(PluginDescriptor(where = PluginDescriptor.WHERE_AUTOSTART, fnc = SoftcamAutostart))
	plist.append(PluginDescriptor(where = PluginDescriptor.WHERE_AUTOSTART, fnc = SwapAutostart))
	plist.append(PluginDescriptor(where = PluginDescriptor.WHERE_SESSIONSTART, fnc = ImageManagerautostart))
	plist.append(PluginDescriptor(where = PluginDescriptor.WHERE_SESSIONSTART, fnc = BackupManagerautostart))
	if config.misc.firstrun.value and not config.misc.restorewizardrun.value and backupAvailable == 1:
		plist.append(PluginDescriptor(name=_("Restore Wizard"), where = PluginDescriptor.WHERE_WIZARD, needsRestart = False, fnc=(2, RestoreWizard)))
	plist.append(PluginDescriptor(name=_("Ipkg"), where = PluginDescriptor.WHERE_FILESCAN, needsRestart = False, fnc = filescan))
	return plist

