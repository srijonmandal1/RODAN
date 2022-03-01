import dbus
import dbus.mainloop.glib

global mainloop

dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

bus = dbus.SystemBus()

adapter_props = dbus.Interface(bus.get_object('org.bluez', '/org/bluez/hci0'),
                                   "org.freedesktop.DBus.Properties");

adapter_props.Set("org.bluez.Adapter1", "Discoverable", dbus.Boolean(1))
