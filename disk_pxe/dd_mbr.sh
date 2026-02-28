#!/bin/bash

# Target device (Adjust to your actual system disk, e.g., /dev/sda)
TARGET_DISK="/dev/sda"
CONTROLLER_ID=0
VIRTUAL_DRIVE_ID=0

# 1. Check if storcli is installed
if ! command -v storcli &> /dev/null; then
    echo "Error: storcli command not found. Please install it first."
    exit 1
fi

echo "--- Starting Precision Disk Wipe ---"

# Check if the device exists
if [ ! -b "$TARGET_DISK" ]; then
    echo "Error: Device $TARGET_DISK not found."
    exit 1
fi

echo "Processing Disk: $TARGET_DISK"

# 2. Set RAID Cache Policy to Write Through (WT)
# This ensures data is written directly to the physical disks during DD
echo "Setting Cache Policy to Write Through..."
storcli /c$CONTROLLER_ID/v$VIRTUAL_DRIVE_ID set wrcache=wt > /dev/null

# 3. Get the total number of sectors (LBA) on the disk
# blockdev --getsz returns the count of 512-byte sectors
TOTAL_SECTORS=$(blockdev --getsz "$TARGET_DISK")
echo "Disk: $TARGET_DISK | Total Sectors: $TOTAL_SECTORS"


# 4. Wipe Primary GPT and MBR (LBA 0 to 33)
# This clears the Protective MBR and the Primary GPT Header/Table.
# This remains well below your board data starting at block 1024.
echo "Wiping Primary GPT (Disk Header)..."
dd if=/dev/zero of="$TARGET_DISK" bs=512 count=34 conv=fdatasync status=none

# 5. Wipe Secondary GPT (Backup Header at the end of the disk)
# Modern kernels (5.x+) can auto-recover partitions if the backup GPT is intact.
# The backup GPT occupies the last 33 sectors of the disk.
BACKUP_START=$((TOTAL_SECTORS - 33))
echo "Wiping Secondary GPT (LBA $BACKUP_START to end)..."
dd if=/dev/zero of="$TARGET_DISK" bs=512 seek=$BACKUP_START count=33 conv=fdatasync status=none

# 6. Force MegaRAID Hardware Cache Flush
# This is critical for 'reboot -f' because it ensures the zeroed blocks 
# move from the RAID card's RAM to the physical platters/NAND.
echo "Flushing MegaRAID Controller Cache..."

storcli /c$CONTROLLER_ID flushcache > /dev/null

# 7. OS Level Sync and Cache Drop
sync
echo 3 > /proc/sys/vm/drop_caches

# 8. Restore Cache Policy to Write Back (WB)
# This ensures the new OS installation via PXE has optimal write performance
echo "Restoring Cache Policy to Write Back for next OS installation..."
storcli /c$CONTROLLER_ID/v$VIRTUAL_DRIVE_ID set wrcache=wb > /dev/null

echo "Wipe complete. Disk headers destroyed. Ready for PXE boot."

# Optional: Force immediate reboot
# reboot -f
