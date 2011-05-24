################################################################################
#
# This program is part of the WMIPerf_Windows Zenpack for Zenoss.
# Copyright (C) 2010, 2011 Egor Puzanov.
#
# This program can be used under the GNU General Public License version 2
# You can find full information here: http://www.zenoss.com/oss
#
################################################################################

__doc__="""DiskDriveMap

DiskDriveMap maps Win32_DiskDrive class to HardDisk class.

$Id: DiskDriveMap.py,v 1.8 2011/05/23 22:53:25 egor Exp $"""

__version__ = '$Revision: 1.8 $'[11:-2]


from ZenPacks.community.WMIDataSource.WMIPlugin import WMIPlugin
from Products.DataCollector.plugins.DataMaps import MultiArgs

class DiskDriveMap(WMIPlugin):
    """Map Win32_DiskDrive class to HardDisk"""

    maptype = "HardDiskMap"
    modname = "ZenPacks.community.WMIPerf_Windows.Win32DiskDrive"
    relname = "harddisks"
    compname = "hw"

    tables = {
        "Win32_DiskDrive": (
            "Win32_DiskDrive",
            None,
            "root/cimv2",
            {
                '__path':'snmpindex',
                'Caption':'description',
                'Index':'id',
                'InterfaceType':'diskType',
                'Manufacturer':'_manuf',
                'MediaType':'_mediatype',
                'Model':'_model',
                'SCSILogicalUnit':'bay',
                'Size':'size',
            },
        ),
        "Win32_PerfRawData_PerfDisk_PhysicalDisk": (
            "Win32_PerfRawData_PerfDisk_PhysicalDisk",
            None,
            "root/cimv2",
            {
                '__path':'snmpindex',
                'Name':'name',
            },
        ),
    }

    def process(self, device, results, log):
        """collect WMI information from this device"""
        log.info('processing %s for device %s', self.name(), device.id)
        rm = self.relMap()
        perfnames = {}
        for inst in results.get("Win32_PerfRawData_PerfDisk_PhysicalDisk", []):
            snmpindex = str(inst.get('snmpindex', ''))
            if snmpindex.find('.') > snmpindex.find(':') > 0:
                snmpindex = snmpindex.split(':', 1)[1]
            perfnames[str(inst.get('name', '')).split()[0]] = snmpindex
        for instance in results.get("Win32_DiskDrive", []):
            om = self.objectMap(instance)
            try:
                om.id = self.prepId('PHYSICALDRIVE%s'%om.id)
                if not om._mediatype or not om._mediatype.startswith('Fixed'):
                    continue
                om.perfindex = perfnames.get(str(instance['id']), None)
                if not om.perfindex: continue
                if om._model and not om._manuf: om._manuf = om._model.split()[0]
                if not om._manuf: om._manuf = 'Unknown'
                if om._model: om.setProductKey = MultiArgs(om._model, om._manuf)
                if om.snmpindex.find('.') > om.snmpindex.find(':') > 0:
                    om.snmpindex = om.snmpindex.split(':', 1)[1]
            except AttributeError:
                raise
            rm.append(om)
        return rm
