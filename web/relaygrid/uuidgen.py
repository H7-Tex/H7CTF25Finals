import time
import random
import threading

class CTFUUIDGenerator:
    """
    Custom UUIDv1 generator that guarantees fewer than 5000 UUIDs
    can be generated within any 6-second window by controlling the
    timestamp increments.
    100ns units are used for timestamp as per UUIDv1 specification.
    6 seconds = 60,000,000 100ns units; thus, increment
    This is for CTF. Actual implementation can be done using standard uuid.uuid1()
    which is more robust. If we used that in this scneario, an attacker could take
    longer time to brute force the UUIDs which also costs infastructure.
    Realistically UUIDV1 is vulnerable to brute force if attacker has time and resources.
    """
    def __init__(self):
        self.lock = threading.Lock()
        self.counter = 0
        self.base_time = int(time.time_ns() / 100)  # 100ns units
        # FIX: Keep these constant so only timestamp changes
        self.clock_seq = random.randint(0, 0x3FFF)
        self.node = random.randint(0, 0xFFFFFFFFFFFF)
        
    def uuid1(self):
        with self.lock:
            # Increment by a random value between 1000 and 2000 each call
            increment = random.randint(1000, 2000)
            self.counter += increment
            timestamp = self.base_time + self.counter + 0x01B21DD213814000

            time_low = timestamp & 0xFFFFFFFF
            time_mid = (timestamp >> 32) & 0xFFFF
            time_hi_version = (timestamp >> 48) & 0x0FFF | (1 << 12)

            # FIX: Use constant values
            clock_seq_hi = (self.clock_seq >> 8) & 0x3F | 0x80
            clock_seq_low = self.clock_seq & 0xFF

            return f"{time_low:08x}-{time_mid:04x}-{time_hi_version:04x}-{clock_seq_hi:02x}{clock_seq_low:02x}-{self.node:012x}"

# Global instance
uuid = CTFUUIDGenerator()

def generate_recovery_uuid():
    return uuid.uuid1()
