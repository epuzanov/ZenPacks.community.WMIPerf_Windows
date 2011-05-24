################################################################################
#
# This program is part of the WMIPerf_Windows Zenpack for Zenoss.
# Copyright (C) 2010, 2011 Egor Puzanov.
#
# This program can be used under the GNU General Public License version 2
# You can find full information here: http://www.zenoss.com/oss
#
################################################################################

__doc__="""DeviceMap

DeviceMap maps CIM_ComputerSystem and CIM_OperationSystem classes to get hw and
os products.

$Id: DeviceMap.py,v 1.4 2011/05/23 23:45:18 egor Exp $"""

__version__ = '$Revision: 1.4 $'[11:-2]


from ZenPacks.community.WMIDataSource.WMIPlugin import WMIPlugin
from Products.DataCollector.plugins.DataMaps import MultiArgs, ObjectMap

class DeviceMap(WMIPlugin):
    """DeviceMap maps CIM_ComputerSystem and CIM_OperationSystem classes to get hw and
       os products.
    """

    maptype = "DeviceMap" 

    tables = {
        "Win32_ComputerSystem": (
            "Win32_ComputerSystem",
            None,
            "root/cimv2",
            {
                'IdentifyingDescriptions':'snmpDescr',
                'Manufacturer':'_manufacturer',
                'Model':'_model',
                'DNSHostName':'snmpSysName',
                'PrimaryOwnerContact': 'snmpContact',
            },
        ),
        "Win32_OperatingSystem": (
            "Win32_OperatingSystem",
            None,
            "root/cimv2",
            {
                'Name':'_name',
                'TotalVisibleMemorySize':'totalMemory',
                'SizeStoredInPagingFiles':'totalSwap',
            },
        ),
        "Win32_SystemEnclosure": (
            "Win32_SystemEnclosure",
            None,
            "root/cimv2",
            {
                'SerialNumber':'sn',
            },
        ),
    }


    def process(self, device, results, log):
        """collect WMI information from this device"""
        log.info('processing %s for device %s', self.name(), device.id)
        try:
            cs = results.get('Win32_ComputerSystem', [None])[0]
            os = results.get('Win32_OperatingSystem', [None])[0]
            if not (cs and os): return
            maps = []
            om = self.objectMap(cs)
            om.snmpLocation = ''
            om.snmpOid = ''
            om.setOSProductKey=MultiArgs(os['_name'].split('|')[0],'Microsoft')
            om.setHWProductKey = MultiArgs(cs['_model'], cs['_manufacturer'])
            sn = str(results.get('Win32_SystemEnclosure',[{'sn':''}])[0]['sn']
                    or '').strip()
            if sn: om.setHWSerialNumber = sn
            maps.append(om)
            maps.append(ObjectMap({"totalMemory":(os.get('totalMemory',0)*1024)}
                                                                ,compname="hw"))
            maps.append(ObjectMap({"totalSwap": (os.get('totalSwap', 0) * 1024)}
                                                                ,compname="os"))
        except:
            log.warning('processing error')
            return
        return maps

