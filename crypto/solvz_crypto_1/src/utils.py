import random
from typing import Tuple


def gcd(a: int, b: int) -> int:
    while b:
        a, b = b, a % b
    return a


def is_coprime(a: int, n: int) -> bool:
    return gcd(a, n) == 1


def get_valid_affine_keys() -> list:
    return [a for a in range(1, 26) if is_coprime(a, 26)]


def mod_inverse(a: int, m: int) -> int:
    for i in range(1, m):
        if (a * i) % m == 1:
            return i
    return None


def encrypt_char(char: str, a: int, b: int) -> str:
    if not char.isalpha():
        return char
    
    char = char.upper()
    x = ord(char) - ord('A')
    encrypted = (a * x + b) % 26
    return chr(encrypted + ord('A'))


def decrypt_char(char: str, a: int, b: int) -> str:
    if not char.isalpha():
        return char
    
    char = char.upper()
    y = ord(char) - ord('A')
    a_inv = mod_inverse(a, 26)
    if a_inv is None:
        raise ValueError(f"No modular inverse for a={a}")
    
    decrypted = (a_inv * (y - b)) % 26
    return chr(decrypted + ord('A'))


def dual_affine_encrypt(plaintext: str, a1: int, b1: int, a2: int, b2: int) -> str:
    ciphertext = []
    for i, char in enumerate(plaintext):
        if i % 2 == 0:
            ciphertext.append(encrypt_char(char, a1, b1))
        else:
            ciphertext.append(encrypt_char(char, a2, b2))
    return ''.join(ciphertext)


def dual_affine_decrypt(ciphertext: str, a1: int, b1: int, a2: int, b2: int) -> str:
    plaintext = []
    for i, char in enumerate(ciphertext):
        if i % 2 == 0:
            plaintext.append(decrypt_char(char, a1, b1))
        else:
            plaintext.append(decrypt_char(char, a2, b2))
    return ''.join(plaintext)


def generate_random_keys(seed: int = None) -> Tuple[int, int, int, int]:
    if seed is not None:
        random.seed(seed)
    
    valid_a_values = get_valid_affine_keys()
    a1 = random.choice(valid_a_values)
    a2 = random.choice(valid_a_values)
    b1 = random.randint(0, 25)
    b2 = random.randint(0, 25)
    
    return a1, b1, a2, b2
