import dbus
import dbus.service
import threading
from gi.repository import GLib
from dbus.mainloop.glib import DBusGMainLoop
DBusGMainLoop(set_as_default=True)
mainLoop = GLib.MainLoop()
bus = dbus.SystemBus()
adapter = bus.get_object("org.bluez", "/org/bluez/hci0")
advertisingManager = dbus.Interface(adapter, "org.bluez.LEAdvertisingManager1" )
advertisingInterface = "org.bluez.LEAdvertisement1"
dbusObjManager = "org.freedesktop.DBus.ObjectManager"
gattService = "org.bluez.GattService1"
gattCharacteristic = "org.bluez.GattCharacteristic1"
gattDescriptor = "org.bluez.GattDescriptor1"
gattManager = dbus.Interface(adapter, "org.bluez.GattManager1")
playPauseCode = 0x01
nextTrackCode = 0x02
previousTrackCode = 0x04
volumeUpCode = 0x08
volumeDownCode = 0x10

def registerSuccess():
    print("Advertisement registered successfully")

def registerError(error):
    print(f"Failed to register advertisement: {error}")

def gattSuccess():
    print("GATT application registered successfully")

def gattError(error):
    print(f"Failed to register GATT application: {error}")

def makeReport(usage):
    return [usage]

class Advertisement(dbus.service.Object):
    def __init__(self, bus, path):
        super().__init__(bus, path)
        self.adType = "peripheral"
        self.localName = "gesturePi"
        self.serviceUUIDs =["1812", "180A", "180F"]

    @dbus.service.method(
        "org.freedesktop.DBus.Properties",
        in_signature="s",
        out_signature="a{sv}"
    )
    def GetAll(self, interface):
        if interface != advertisingInterface:
            return {}
        return {
            "Type": self.adType,
            "LocalName": self.localName,
            "ServiceUUIDs": self.serviceUUIDs
        }

advertisement = Advertisement(bus, "/com/gesture/advertisement0")
advertisingManager.RegisterAdvertisement(
    "/com/gesture/advertisement0",
    {},
    reply_handler=registerSuccess,
    error_handler=registerError
)

class Application(dbus.service.Object):
    def __init__(self, bus, path):
        super().__init__(bus, path)
        self.services = []

    @dbus.service.method(
        "org.freedesktop.DBus.ObjectManager",
        in_signature="",
        out_signature="a{oa{sa{sv}}}"
    )
    def GetManagedObjects(self):
        serviceDict = {}
        for service in self.services:
            serviceDict[dbus.ObjectPath(service.path)] = service.getProperties()
            for characteristic in service.characteristics:
                serviceDict[dbus.ObjectPath(characteristic.path)] = characteristic.getProperties()
                for descriptor in characteristic.descriptors:
                    serviceDict[dbus.ObjectPath(descriptor.path)] = descriptor.getProperties()
        return serviceDict

class Service(dbus.service.Object):
    def __init__(self, bus, path, uuid):
        super().__init__(bus, path)
        self.path = path
        self.uuid = uuid
        self.characteristics = []

    @dbus.service.method(
        "org.freedesktop.DBus.Properties",
        in_signature="s",
        out_signature="a{sv}"
    )
    def GetAll(self, interface):
        if interface != gattService:
            return {}
        return {
            "UUID": dbus.String(self.uuid),
            "Primary": dbus.Boolean(True)
        }

    def getProperties(self):
        return {gattService: self.GetAll(gattService)}

class Characteristic(dbus.service.Object):
    def __init__(self, bus, path, uuid, service, flags):
        super().__init__(bus, path)
        self.path = path
        self.uuid = uuid
        self.service = service
        self.flags = flags
        self.descriptors = []

    @dbus.service.method(
        "org.freedesktop.DBus.Properties",
        in_signature="s",
        out_signature="a{sv}"
    )
    def GetAll(self, interface):
        if interface != gattCharacteristic:
            return {}
        return {
            "UUID": dbus.String(self.uuid),
            "Service": dbus.ObjectPath(self.service.path),
            "Flags": dbus.Array(self.flags, signature="s")
        }

    def getProperties(self):
        return {gattCharacteristic: self.GetAll(gattCharacteristic)}

    @dbus.service.method(
        gattCharacteristic,
        in_signature="a{sv}",
        out_signature="ay"
    )
    def ReadValue(self, options):
        return []

class Descriptor(dbus.service.Object):
    def __init__(self, bus, path, uuid, characteristic, flags):
        super().__init__(bus, path)
        self.path = path
        self.uuid = uuid
        self.characteristic = characteristic
        self.flags = flags

    @dbus.service.method(
        "org.freedesktop.DBus.Properties",
        in_signature="s",
        out_signature="a{sv}"
    )
    def GetAll(self, interface):
        if interface != gattDescriptor:
            return {}
        return {
            "UUID": dbus.String(self.uuid),
            "Characteristic": dbus.ObjectPath(self.characteristic.path),
            "Flags": dbus.Array(self.flags, signature="s")
        }

    def getProperties(self):
        return {gattDescriptor: self.GetAll(gattDescriptor)}

    @dbus.service.method(
        gattDescriptor,
        in_signature="a{sv}",
        out_signature="ay"
    )
    def ReadValue(self, options):
        return []

class HIDInformation(Characteristic):
    def __init__(self, bus, path, service):
        super().__init__(bus, path, "2A4A", service, ["read"])

    @dbus.service.method(
        gattCharacteristic,
        in_signature="a{sv}",
        out_signature="ay"
    )
    def ReadValue(self, options):
        return [0x11, 0x01, 0x00, 0x02]

class ReportMap(Characteristic):
    def __init__(self, bus, path, service):
        super().__init__(
            bus,
            path,
            "2A4B",
            service,
            ["read"]
        )

    @dbus.service.method(
        gattCharacteristic,
        in_signature="a{sv}",
        out_signature="ay"
    )
    def ReadValue(self, options):
        return [
            0x05, 0x0C,
            0x09, 0x01,
            0xA1, 0x01,
            0x85, 0x01,

            0x15, 0x00,
            0x25, 0x01,

            0x09, 0xCD,
            0x09, 0xB5,
            0x09, 0xB6,
            0x09, 0xE9,
            0x09, 0xEA,

            0x75, 0x01,
            0x95, 0x05,
            0x81, 0x02,

            0x75, 0x03,
            0x95, 0x01,
            0x81, 0x03,

            0xC0
        ]

class HIDControlPoint(Characteristic):
    def __init__(self, bus, path, service):
        super().__init__(bus, path, "2A4C", service, ["write-without-response"])

    @dbus.service.method(
        gattCharacteristic,
        in_signature="aya{sv}",
        out_signature=""
    )
    def WriteValue(self, value, options):
        pass

class ProtocolMode(Characteristic):
    def __init__(self, bus, path, service):
        super().__init__(bus, path, "2A4E", service, ["read", "write-without-response"])
        self.value = [0x01]

    @dbus.service.method(
        gattCharacteristic,
        in_signature="a{sv}",
        out_signature="ay"
    )
    def ReadValue(self, options):
        return self.value

    @dbus.service.method(
        gattCharacteristic,
        in_signature="aya{sv}",
        out_signature=""
    )
    def WriteValue(self, value, options):
        self.value = value

class ReportReference(Descriptor):
    def __init__(self, bus, path, characteristic):
        super().__init__(bus, path, "2908", characteristic, ["read"])

    @dbus.service.method(
        gattDescriptor,
        in_signature="a{sv}",
        out_signature="ay"
    )
    def ReadValue(self, options):
        return [0x01, 0x01]

class Report(Characteristic):
    def __init__(self, bus, path, service):
        super().__init__(bus, path, "2A4D", service, ["read", "notify"])
        self.value = [0x00]
        self.notifying = False

    @dbus.service.method(
        gattCharacteristic,
        in_signature="a{sv}",
        out_signature="ay"
    )
    def ReadValue(self, options):
        return self.value

    @dbus.service.method(
        gattCharacteristic,
        in_signature="",
        out_signature=""
    )
    def StartNotify(self):
        self.notifying = True

    @dbus.service.method(
        gattCharacteristic,
        in_signature="",
        out_signature=""
    )
    def StopNotify(self):
        self.notifying = False

    @dbus.service.signal(
            "org.freedesktop.DBus.Properties",
            signature="sa{sv}as",
    )
    def PropertiesChanged(self, interface, changed, invalidated):
        pass

    def sendReport(self, usage):
        if not self.notifying:
            return
        self.value = list(makeReport(usage))
        self.PropertiesChanged(gattCharacteristic, {"Value": dbus.Array(self.value, signature="y")}, [])
        GLib.timeout_add(50, self.releaseReport)
        return False

    def releaseReport(self):
        self.value = [0x00]

        self.PropertiesChanged(
            gattCharacteristic,
            {
                "Value": dbus.Array(
                    self.value,
                    signature="y"
                )
            },
            []
        )

        return False

class PnPID(Characteristic):
    def __init__(self, bus, path, service):
        super().__init__(bus, path, "2A50", service, ["read"])

    @dbus.service.method(
        gattCharacteristic,
        in_signature="a{sv}",
        out_signature="ay"
    )
    def ReadValue(self, options):
        return [
            0x01,
            0xFF, 0xFF,
            0x01, 0x00,
            0x01, 0x00
        ]

class BatteryLevel(Characteristic):
    def __init__(self, bus, path, service):
        super().__init__(bus, path, "2A19", service, ["read"])

    @dbus.service.method(
        gattCharacteristic,
        in_signature="a{sv}",
        out_signature="ay"
    )
    def ReadValue(self, options):
        return [100]

applicationTest = Application(bus, "/com/gesture")

serviceTest = Service(bus, "/com/gesture/service0", "1812")
applicationTest.services.append(serviceTest)
serviceTest.characteristics.append(HIDInformation(bus, "/com/gesture/service0/char0", serviceTest))
serviceTest.characteristics.append(ReportMap(bus, "/com/gesture/service0/char1", serviceTest))
serviceTest.characteristics.append(HIDControlPoint(bus, "/com/gesture/service0/char2", serviceTest))

reportTest = Report(bus, "/com/gesture/service0/char3", serviceTest)
serviceTest.characteristics.append(reportTest)

serviceTest.characteristics.append(ProtocolMode(bus, "/com/gesture/service0/char4", serviceTest))

reportTest.descriptors.append(
    ReportReference(bus, "/com/gesture/service0/char3/desc0", reportTest)
)

deviceInfoService = Service(bus, "/com/gesture/service1", "180A")
applicationTest.services.append(deviceInfoService)
deviceInfoService.characteristics.append(
    PnPID(bus, "/com/gesture/service1/char0", deviceInfoService)
)

batteryService = Service(bus, "/com/gesture/service2", "180F")
applicationTest.services.append(batteryService)
batteryService.characteristics.append(
    BatteryLevel(bus, "/com/gesture/service2/char0", batteryService)
)

gattManager.RegisterApplication(
    "/com/gesture",
    {},
    reply_handler=gattSuccess,
    error_handler=gattError
)
def startBluetooth():
    bluetoothThread = threading.Thread(target=mainLoop.run, daemon=True)
    bluetoothThread.start()

def sendMediaControl(usage):
    GLib.idle_add(reportTest.sendReport, usage)