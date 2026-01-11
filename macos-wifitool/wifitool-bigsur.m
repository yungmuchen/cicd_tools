#import <Foundation/Foundation.h>
#import <CoreWLAN/CoreWLAN.h>
#import <Security/Security.h>

/**
 * wifitool: Updated for macOS 11.0+ (Big Sur through Sonoma)
 * Modernizes CWInterface access and security protocol checks.
 */

int main(int argc, const char * argv[]) {
    @autoreleasepool {
        NSUserDefaults *args = [NSUserDefaults standardUserDefaults];
        NSString *action = [args stringForKey:@"action"];
        NSString *targetSSID = [args stringForKey:@"ssid"];
        NSString *username = [args stringForKey:@"user"];
        NSString *password = [args stringForKey:@"password"];
        // Use 'en1' as default for most modern MacBooks
        NSString *ifName = [args stringForKey:@"interface"] ?: @"en1";

        if (!action) {
            printf("Usage: wifitool -action <connect|disconnect|scan> [-ssid <ssid>] [-user <uid>] [-password <pwd>] [-interface <en1>]\n");
            return 1;
        }

        // Modern practice: Always use the shared client to avoid sandbox/permission issues
        CWWiFiClient *client = [CWWiFiClient sharedWiFiClient];
        CWInterface *interface = [client interfaceWithName:ifName];
        
        if (!interface) {
            fprintf(stderr, "[Error] Interface %s not found.\n", [ifName UTF8String]);
            return 1;
        }

        // --- SCAN ACTION ---
        if ([action isEqualToString:@"scan"]) {
            NSError *error = nil;
            // Modern scan API; passing nil for name returns all visible networks
            NSSet<CWNetwork *> *networks = [interface scanForNetworksWithName:targetSSID error:&error];
            
            if (error) {
                fprintf(stderr, "[Error] Scan failed: %s\n", [[error localizedDescription] UTF8String]);
                return 1;
            }

            printf("%-32s %-6s %-4s %-12s\n", "SSID", "RSSI", "CH", "SECURITY");
            printf("----------------------------------------------------------------------\n");
            
            for (CWNetwork *network in networks) {
                NSString *ssid = network.ssid ?: @"<Hidden>";
                printf("%-32s %-6ld %-4ld ", [ssid UTF8String], (long)network.rssiValue, (long)network.wlanChannel.channelNumber);
                
                // Updated Security checks for WPA3/WPA2 Enterprise
                if ([network supportsSecurity:kCWSecurityWPA3Enterprise]) printf("WPA3-Ent");
                else if ([network supportsSecurity:kCWSecurityWPA3Personal]) printf("WPA3-Pers");
                else if ([network supportsSecurity:kCWSecurityWPA2Enterprise]) printf("WPA2-Ent");
                else if ([network supportsSecurity:kCWSecurityWPA2Personal]) printf("WPA2-Pers");
                else if ([network supportsSecurity:kCWSecurityNone]) printf("None");
                else printf("Other");
                printf("\n");
            }
            return 0;
        }

        // --- DISCONNECT ACTION ---
        if ([action isEqualToString:@"disconnect"]) {
            [interface disassociate];
            printf("[Success] Disassociated from network on %s.\n", [ifName UTF8String]);
            return 0;
        }

        // --- CONNECT ACTION ---
        if ([action isEqualToString:@"connect"]) {
            if (!targetSSID) {
                fprintf(stderr, "[Error] -ssid is required for connection.\n");
                return 1;
            }

            NSError *error = nil;
            // Fetch the specific network object needed for association
            NSSet *networks = [interface scanForNetworksWithName:targetSSID error:&error];
            CWNetwork *network = [networks anyObject];

            if (!network) {
                fprintf(stderr, "[Error] Could not find SSID '%s'.\n", [targetSSID UTF8String]);
                return 1;
            }

            BOOL success = NO;
            if (username && username.length > 0) {
                // Modern Enterprise Association: macOS 11+ relies heavily on this for 802.1X
                success = [interface associateToEnterpriseNetwork:network 
                                                         identity:nil 
                                                         username:username 
                                                         password:password 
                                                            error:&error];
            } else {
                // Standard Association
                success = [interface associateToNetwork:network 
                                               password:password 
                                                  error:&error];
            }

            if (success) {
                printf("[Success] Connected to %s\n", [targetSSID UTF8String]);
            } else {
                fprintf(stderr, "[Failed] %s\n", [[error localizedDescription] UTF8String]);
                return 1;
            }
        }
    }
    return 0;
}
