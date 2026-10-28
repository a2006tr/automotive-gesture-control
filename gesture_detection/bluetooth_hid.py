import dbus
import dbus.service
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
gattManager = dbus.Interface(adapter, "org.bluez.GattManager1")
playPause = 0x00CD
nextTrack = 0x00B5
previousTrack = 0x00B6
volumeUp = 0x00E9
volumeDown = 0x00EA
def registerSuccess():
    print("Advertisement registered successfully")
def registerError(error):
    print(f"Failed to register advertisement: {error}")
def makeReport(usage):
    return usage.to_bytes(2, byteorder="little")
class Advertisement(dbus.service.Object):
    def __init__(self, bus, path):
        super().__init__(bus, path)
        self.adType = "peripheral"
        self.localName = "gesturePi"
        self.serviceUUIDs =["1812"]
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
            serviceDict[service.path] = service.getProperties()
            for characteristic in service.characteristics:
                serviceDict[characteristic.path] = characteristic.getProperties()
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
            "UUID": self.uuid,
            "Primary": True
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
    @dbus.service.method(
        "org.freedesktop.DBus.Properties",
        in_signature="s",
        out_signature="a{sv}"
    )
    def GetAll(self, interface):
        if interface != gattCharacteristic:
            return {}
        return {
            "UUID": self.uuid,
            "Service": self.service.path,
            "Flags": self.flags
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
applicationTest = Application(bus, "/com/gesture")
serviceTest = Service(bus, "/com/gesture/service0", "1812")
#characteristicTest = Characteristic(bus, "/com/gesture/service0/characteristic0", "2A37", serviceTest, ["read", "notify"])
applicationTest.services.append(serviceTest)
mainLoop.run()
