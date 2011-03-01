################################################################################
#
# This program is part of the WMIPerf_Windows Zenpack for Zenoss.
# Copyright (C) 2010 Egor Puzanov.
#
# This program can be used under the GNU General Public License version 2
# You can find full information here: http://www.zenoss.com/oss
#
################################################################################

__doc__="""FileSystemMap

FileSystemMap maps the Win32_FileSystem class to filesystems objects

$Id: FileSystemMap.py,v 1.7 2011/03/01 23:59:19 egor Exp $"""

__version__ = '$Revision: 1.7 $'[11:-2]

import re
from ZenPacks.community.WMIDataSource.WMIPlugin import WMIPlugin

class FileSystemMap(WMIPlugin):

    maptype = "FileSystemMap"
    compname = "os"
    relname = "filesystems"
    modname = "Products.ZenModel.FileSystem"
    deviceProperties = WMIPlugin.deviceProperties + (
      'zFileSystemMapIgnoreNames', 'zFileSystemMapIgnoreTypes')

    tables = {
            "Win32_LogicalDisk":
                (
                "Win32_LogicalDisk",
                None,
                "root/cimv2",
                    {
                    '__path':'snmpindex',
                    'BlockSize':'blockSize',
                    'FileSystem':'type',
                    'MaximumComponentLenght':'maxNameLen',
                    'Name':'mount',
                    'Size':'totalBlocks',
                    }
                ),
            }

    def process(self, device, results, log):
        """collect WMI information from this device"""
        log.info('processing %s for device %s', self.name(), device.id)
        rm = self.relMap()
        skipfsnames = getattr(device, 'zFileSystemMapIgnoreNames', None)
        skipfstypes = getattr(device, 'zFileSystemMapIgnoreTypes', None)
        for instance in results.get("Win32_LogicalDisk", []):
            try:
                if skipfsnames and re.search(skipfsnames, instance['mount']):
                    log.info("Skipping %s as it matches zFileSystemMapIgnoreNames.",
                        instance['mount'])
                    continue
                if skipfstypes and instance['type'] in skipfstypes:
                    log.info("Skipping %s (%s) as it matches zFileSystemMapIgnoreTypes.",
                        instance['mount'], instance['type'])
                    continue
                om = self.objectMap(instance)
                om.id = self.prepId(om.mount)
                if ':' in om.snmpindex:om.snmpindex=om.snmpindex.split(':',1)[1]
                om.blockSize = getattr(om, 'blockSize', 4096) or 4096
                if not om.totalBlocks: continue
                om.totalBlocks = om.totalBlocks / om.blockSize
            except AttributeError:
                continue
            rm.append(om)
        return rm
