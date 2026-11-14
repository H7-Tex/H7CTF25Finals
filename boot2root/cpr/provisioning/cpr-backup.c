#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <grp.h>

#define BACKUP_DIR "/opt/cpr/backups"
#define DATA_DIR "/opt/cpr/data"

int main(int argc, char *argv[]) {
    char command[512];
    uid_t euid;
    gid_t egid;
    
    // Get effective IDs
    euid = geteuid();  // abu's UID (2002)
    egid = getegid();  // platform-admins GID (1100)
    
    // Permanently elevate to owner's privileges (abu)
    // Set all GIDs (real, effective, saved) to effective GID
    setresgid(egid, egid, egid);
    
    // Set all UIDs (real, effective, saved) to effective UID
    setresuid(euid, euid, euid);
    
    if (argc != 2) {
        printf("Usage: cpr-backup <backup_name>\n");
        printf("Creates a backup of CPR data directory\n");
        return 1;
    }
    
    char *backup_name = argv[1];
    
    // Ensure backup directory exists
    mkdir(BACKUP_DIR, 0775);
    
    // Print status message
    printf("[*] Creating backup: %s\n", backup_name);
    
    // Build tar command to create compressed backup
    sprintf(command, "cd %s && tar -czf %s/%s.tar.gz . 2>/dev/null", 
            DATA_DIR, BACKUP_DIR, backup_name);
    
    // Execute backup command
    system(command);
    
    printf("[+] Backup created: %s/%s.tar.gz\n", BACKUP_DIR, backup_name);
    
    return 0;
}
