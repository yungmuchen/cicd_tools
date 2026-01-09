import Foundation
import CoreWLAN

let args = CommandLine.arguments

let client = CWWiFiClient.shared()

let interface: CWInterface?

if args.count > 1 {
    let ifname = args[1]
    interface = client.interface(withName: ifname)

    if interface == nil {
        fputs("ERROR: Wi-Fi interface '\(ifname)' not found\n", stderr)
        exit(1)
    }
} else {
    interface = client.interface()
}

guard let wifi = interface else {
    fputs("ERROR: No Wi-Fi interface available\n", stderr)
    exit(1)
}

do {
    let networks = try wifi.scanForNetworks(withName: nil)

    print("Interface: \(wifi.interfaceName ?? "-")")
    print("SSID\t\tBSSID\t\t\tRSSI\tChannel\tSecurity")
    print("---------------------------------------------------------------------")

    for network in networks {
        let ssid = network.ssid ?? "<hidden>"
        let bssid = network.bssid ?? "-"
        let rssi = network.rssiValue
        let channel = network.wlanChannel?.channelNumber ?? 0

        let security: String
        if network.supportsSecurity(.wpa3Personal) ||
           network.supportsSecurity(.wpa3Enterprise) {
            security = "WPA3"
        } else if network.supportsSecurity(.wpa2Personal) ||
                  network.supportsSecurity(.wpa2Enterprise) {
            security = "WPA2"
        } else {
            security = "OPEN"
        }

        print("\(ssid)\t\(bssid)\t\(rssi)\t\(channel)\t\(security)")
    }

} catch {
    fputs("Scan failed: \(error)\n", stderr)
    exit(2)
}
