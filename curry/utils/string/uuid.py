import hashlib
import uuid


def deterministic_uuid_v4(input_string: str) -> uuid.UUID:
    # Hash the input string using SHA-256 (or another hash function)
    hash_value = hashlib.sha256(input_string.encode()).hexdigest()

    # Take the first 32 characters of the hash and format them as a UUID
    # UUID v4 has specific bits set, so we need to modify the resulting hash accordingly
    hash_value = list(hash_value)

    # Set the UUID version to 4 (the version field is the 13th hexadecimal digit)
    hash_value[12] = "4"

    # Set the two most significant bits of the 17th hexadecimal digit to '10' (for UUID variant)
    hash_value[16] = format((int(hash_value[16], 16) & 0x3) | 0x8, "x")

    # Join the list into a valid UUID string
    uuid_string = "".join(hash_value[:32])

    # Return the UUID
    return uuid.UUID(uuid_string)


if __name__ == "__main__":
    # Example usage
    input_str = "example input"
    det_uuid = deterministic_uuid_v4(input_str)
    print(det_uuid)
