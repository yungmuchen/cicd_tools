import Foundation
import CoreWLAN
// development env: macOS 10.15, Xcode 11.7
// mac-mini (os 10.15) connect to a 8021x WLAN. Cert for radius server already approved before.
// This program does not handle cert approvement pop-up windows.
// MARK: - Usage

func usageAndExit() -> Never {
    print("""
    Usage:
      wifitool -action <connect|disconnect> -ssid <ssid>
               [-user <user> -password <password>]
               [-iface <interface>]

    Examples:
      Connect (default en1):
        sudo wifitool -action connect -ssid CorpWiFi -user test -password secret

      Connect (specified iface):
        sudo wifitool -action connect -ssid CorpWiFi -iface en0 -user test -password secret

      Disconnect:
        sudo wifitool -action disconnect -ssid CorpWiFi
    """)
    exit(1)
}

// MARK: - Argument Parsing

let args = CommandLine.arguments

func value(for flag: String) -> String? {
    guard let idx = args.firstIndex(of: flag),
          idx + 1 < args.count else {
        return nil
    }
    return args[idx + 1]
}

guard let action = value(for: "-action"),
      let ssid = value(for: "-ssid") else {
    usageAndExit()
}

let username = value(for: "-user")
let password = value(for: "-password")
let ifaceName = value(for: "-iface") ?? "en1"

// MARK: - Wi-Fi Interface

let client = CWWiFiClient.shared()

guard let interfaces = client.interfaces() else {
    print("No Wi-Fi interfaces found")
    exit(2)
}

guard let iface = interfaces.first(where: { $0.interfaceName == ifaceName }) else {
    print("Wi-Fi interface '\(ifaceName)' not found")
    print("Available interfaces:")
    for i in interfaces {
        print("  - \(i.interfaceName ?? "unknown")")
    }
    exit(2)
}

print("Using interface: \(iface.interfaceName ?? "unknown")")

// MARK: - Actions

switch action.lowercased() {

case "connect":

    guard let user = username, let pass = password else {
        print("-user and -password are required for connect")
        usageAndExit()
    }

    do {
        print("Scanning for SSID: \(ssid)")
        let ssidData = ssid.data(using: .utf8)

        let networks = try iface.scanForNetworks(withSSID: ssidData)

        guard let network = networks.first else {
            print("SSID not found")
            exit(3)
        }

        print("Connecting to \(network.ssid ?? ssid) using 802.1X")

        try iface.associate(
            toEnterpriseNetwork: network,
            identity: nil,
            username: user,
            password: pass
        )

        print("Connection request sent")

    } catch {
        print("Connect failed: \(error.localizedDescription)")
        exit(4)
    }

case "disconnect":

    let currentSSID = iface.ssid()

    guard let cur = currentSSID else {
        print("Not connected to Wi-Fi")
        exit(0)
    }

    if cur == ssid || ssid.isEmpty {
        print("Disconnecting from \(cur)")
        iface.disassociate()
        print("Disconnected")
    } else {
        print("Connected to \(cur), not \(ssid)")
    }

default:
    print("Invalid action: \(action)")
    usageAndExit()
}

