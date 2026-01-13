#import <Foundation/Foundation.h>
#import <CoreWLAN/CoreWLAN.h>
#import <Security/Security.h>

/**
 * wifitool: A command-line utility to manage 802.1X Enterprise Wi-Fi connections.
 * Supports: connect, disconnect, scan
 * Targets: macOS 10.15 ~ 13. sw_vers < 14.
 */
 
int main(int argc, const char * argv[]) {
    @autoreleasepool {
        NSUserDefaults *args = [NSUserDefaults standardUserDefaults];
        NSString *action = [args stringForKey:@"action"];
        NSString *targetSSID = [args stringForKey:@"ssid"];
        NSString *username = [args stringForKey:@"user"];
        NSString *password = [args stringForKey:@"password"];
        NSString *ifName = [args stringForKey:@"interface"] ?: @"en1";

        if (!action) {
            printf("Usage: wifitool -action <connect|disconnect|scan> [-ssid <ssid>] [-user <uid>] [-password <pwd>] [-interface <en1>]\n");
            return 1;
        }

        CWWiFiClient *client = [CWWiFiClient sharedWiFiClient];
        CWInterface *interface = [client interfaceWithName:ifName];
        
        if (!interface) {
            NSLog(@"[Error] Interface %@ not found.", ifName);
            return 1;
        }

        // --- SCAN ACTION ---
        if ([action isEqualToString:@"scan"]) {
            NSError *error = nil;
            // Scanning for nil returns all visible networks
            NSSet<CWNetwork *> *networks = [interface scanForNetworksWithName:targetSSID error:&error];
            
            if (error) {
                NSLog(@"[Error] Scan failed: %@", error.localizedDescription);
                return 1;
            }

            printf("%-32s %-10s %-10s %-10s\n", "SSID", "RSSI", "CH", "SECURITY");
            printf("----------------------------------------------------------------------\n");
            
            for (CWNetwork *network in networks) {
                // If targetSSID was provided, scanForNetworksWithName already filtered it, 
                // but we iterate to print details.
                NSString *ssid = network.ssid ?: @"<Hidden>";
                long rssi = (long)network.rssiValue;
                long channel = (long)network.wlanChannel.channelNumber;
                
                printf("%-32s %-10ld %-10ld ", [ssid UTF8String], rssi, channel);
                
                if ([network supportsSecurity:kCWSecurityWPA3Enterprise]) printf("WPA3-Ent ");
                else if ([network supportsSecurity:kCWSecurityWPA3Personal]) printf("WPA3-Pers ");
                else if ([network supportsSecurity:kCWSecurityWPA2Enterprise]) printf("WPA2-Ent ");
                else if ([network supportsSecurity:kCWSecurityWPA2Personal]) printf("WPA2-Pers ");
                else printf("Other ");
                printf("\n");
            }
            return 0;
        }

        // --- DISCONNECT ACTION ---
        if ([action isEqualToString:@"disconnect"]) {
            [interface disassociate];
            NSLog(@"[Success] Disassociated from network on %@.", ifName);
            return 0;
        }

        // --- CONNECT ACTION ---
        if ([action isEqualToString:@"connect"]) {
            if (!targetSSID) {
                NSLog(@"[Error] -ssid is required for connection.");
                return 1;
            }

            NSError *error = nil;
            NSSet *networks = [interface scanForNetworksWithName:targetSSID error:&error];
            CWNetwork *network = [networks anyObject];

            if (!network) {
                NSLog(@"[Error] Could not find SSID '%@'.", targetSSID);
                return 1;
            }

            BOOL success = NO;
            if (username && username.length > 0) {
                success = [interface associateToEnterpriseNetwork:network identity:nil username:username password:password error:&error];
            } else {
                success = [interface associateToNetwork:network password:password error:&error];
            }

            if (success) {
                NSLog(@"[Success] Connected to %@", targetSSID);
            } else {
                NSLog(@"[Failed] %@", error.localizedDescription);
                return 1;
            }
        }
    }
    return 0;
}
