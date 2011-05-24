################################################################################
#
# This program is part of the WMIPerf_Windows Zenpack for Zenoss.
# Copyright (C) 2010, 2011 Egor Puzanov.
#
# This program can be used under the GNU General Public License version 2
# You can find full information here: http://www.zenoss.com/oss
#
################################################################################

__doc__="""NewDeviceMap

DeviceMap maps CIM_ComputerSystem and CIM_OperationSystem classes to get hw and
os products.

$Id: NewDeviceMap.py,v 1.4 2011/05/23 23:59:51 egor Exp $"""

__version__ = '$Revision: 1.4 $'[11:-2]


from ZenPacks.community.WMIDataSource.WMIPlugin import WMIPlugin
from Products.DataCollector.plugins.DataMaps import MultiArgs

class NewDeviceMap(WMIPlugin):
    """
    Record basic hardware/software information based on the Win32_ComputerSystem
    and Win32_OperatingSystem.
    """

    maptype = "NewDeviceMap" 

    tables = {
        "Win32_ComputerSystem": (
            "Win32_ComputerSystem",
            None,
            "root/cimv2",
            {
                'Manufacturer':'_manuf',
                'Model':'_model',
            },
        ),
        "Win32_OperatingSystem": (
            "Win32_OperatingSystem",
            None,
            "root/cimv2",
            {
                'Name':'_name',
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
            if not (os and os): return
            om = self.objectMap()
            om.setHWProductKey = MultiArgs(cs['_model'], cs['_manuf'])
            om.setOSProductKey=MultiArgs(os['_name'].split('|')[0],'Microsoft')
            sn = str(results.get('Win32_SystemEnclosure',[{'sn':''}])[0]['sn']
                    or '').strip()
            if sn: om.setHWSerialNumber = sn
        except:
            return
        return om

