import sys
import os
import socket
import uvicorn


def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip


def generate_certs_if_needed():
    """Only generate SSL certs if they don't already exist."""
    if os.path.exists("key.pem") and os.path.exists("cert.pem"):
        print("✅ SSL certificates already exist. Skipping generation.")
        return

    print("🔐 Generating local SSL certificates...")
    import datetime
    import ipaddress
    from cryptography import x509
    from cryptography.x509.oid import NameOID
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa

    ip_addr = get_local_ip()
    print(f"   Certificate IP: {ip_addr}")

    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    subject = issuer = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, ip_addr)])
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.datetime.now(datetime.timezone.utc))
        .not_valid_after(datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=365))
        .add_extension(x509.SubjectAlternativeName([x509.IPAddress(ipaddress.ip_address(ip_addr))]), critical=False)
        .sign(key, hashes.SHA256())
    )

    with open("key.pem", "wb") as f:
        f.write(key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.TraditionalOpenSSL, serialization.NoEncryption()))
    with open("cert.pem", "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))

    print("✅ SSL certificates generated successfully!")


if __name__ == "__main__":
    generate_certs_if_needed()

    ip = get_local_ip()
    print()
    print("=" * 55)
    print("  🎥  MCX Cam — Local Network Camera App")
    print("=" * 55)
    print(f"  📱 Sender (Mobile) : https://{ip}:8000/sender.html")
    print(f"  💻 Viewer (Desktop): https://{ip}:8000/viewer.html")
    print()
    print("  ⚠️  On first visit, click 'Advanced → Proceed'")
    print("     to bypass the self-signed cert warning.")
    print("=" * 55)
    print()

    from main import app
    uvicorn.run(app, host="0.0.0.0", port=8000, ssl_keyfile="key.pem", ssl_certfile="cert.pem")

