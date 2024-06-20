import atexit
import hashlib
import os.path
import platform
import re
from setuptools import setup
import shutil
import tarfile
import tempfile
import urllib.request

setupDir = os.path.dirname(__file__)
with open(os.path.join(setupDir, ".version.hadolint")) as vH:
    hadolint_version = vH.read().strip()

machine = platform.machine()
if machine == "x86_64":
    cabal_machine = "x86_64"
elif machine == "aarch64":
    cabal_machine = "arm64"
else:
    cabal_machine = machine
system = platform.system()
hadolint_remote_name=f"hadolint-{system}-{cabal_machine}"
hadolint_download_link = f"https://github.com/hadolint/hadolint/releases/download/v{hadolint_version}/{hadolint_remote_name}"
hadolint_download_link_sha256 = hadolint_download_link + ".sha256"

# Fetch the binary and the checksum to a temporary place
edir = tempfile.mkdtemp()
atexit.register(shutil.rmtree, edir)
the_hadolint_path_sha256 = os.path.join(edir, "hadolint.sha256")
_, headers = urllib.request.urlretrieve(hadolint_download_link_sha256, filename=the_hadolint_path_sha256)
the_hadolint_path = os.path.join(edir, "hadolint")
_, headers = urllib.request.urlretrieve(hadolint_download_link, filename=the_hadolint_path)

# Validate the checksum
# inspired on https://gist.github.com/airtower-luna/a5df5d6143c8e9ffe7eb5deb5797a0e0
sumpat = re.compile(r'(^[0-9A-Fa-f]+)\s+(\S.*)$')
with open(the_hadolint_path_sha256, mode="r", encoding="utf-8") as fH:
    for line in fH:
        m = sumpat.match(line)
        if m:
            checksum = m.group(1)
            filename = m.group(2)
            # Only check what it is needed
            if filename in ("*" + hadolint_remote_name, hadolint_remote_name):
                h = hashlib.sha256()
                with open(the_hadolint_path, mode="rb") as fh:
                    while True:
                        data = fh.read(1024*1024)
                        if len(data) == 0:
                            break
                        else:
                            h.update(data)
                if checksum != h.hexdigest():
                    raise Exception(f"hadolint {hadolint_version} checksum does not match!")

# Assuring the right permissions
os.chmod(the_hadolint_path, 0o555)

setup(
    name='pre_commit_placeholder_package',
    version=hadolint_version,
    data_files=[
        ("bin", [the_hadolint_path])
    ]
)
