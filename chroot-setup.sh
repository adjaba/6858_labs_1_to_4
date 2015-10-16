#!/bin/sh -x
if id | grep -qv uid=0; then
    echo "Must run setup as root"
    exit 1
fi

create_socket_dir() {
    local dirname="$1"
    local ownergroup="$2"
    local perms="$3"

    mkdir -p $dirname
    chown $ownergroup $dirname
    chmod $perms $dirname
}

set_perms() {
    local ownergroup="$1"
    local perms="$2"
    local pn="$3"

    chown $ownergroup $pn
    chmod $perms $pn
}

rm -rf /jail
mkdir -p /jail
cp -p index.html /jail

./chroot-copy.sh zookd /jail
./chroot-copy.sh zookfs /jail

#./chroot-copy.sh /bin/bash /jail

./chroot-copy.sh /usr/bin/env /jail
./chroot-copy.sh /usr/bin/python /jail

# to bring in the crypto libraries
./chroot-copy.sh /usr/bin/openssl /jail

mkdir -p /jail/usr/lib /jail/usr/lib/i386-linux-gnu /jail/lib /jail/lib/i386-linux-gnu
cp -r /usr/lib/python2.7 /jail/usr/lib
cp /usr/lib/i386-linux-gnu/libsqlite3.so.0 /jail/usr/lib/i386-linux-gnu
cp /lib/i386-linux-gnu/libnss_dns.so.2 /jail/lib/i386-linux-gnu
cp /lib/i386-linux-gnu/libresolv.so.2 /jail/lib/i386-linux-gnu
cp -r /lib/resolvconf /jail/lib

mkdir -p /jail/usr/local/lib
cp -r /usr/local/lib/python2.7 /jail/usr/local/lib

mkdir -p /jail/etc
cp /etc/localtime /jail/etc/
cp /etc/timezone /jail/etc/
cp /etc/resolv.conf /jail/etc/

mkdir -p /jail/usr/share/zoneinfo
cp -r /usr/share/zoneinfo/America /jail/usr/share/zoneinfo/

create_socket_dir /jail/echosvc 61010:61010 755
# For Cred DB
create_socket_dir /jail/authsvc 71010:71010 755
# For bank DB
create_socket_dir /jail/banksvc 81010:81010 755
# For profile service
create_socket_dir /jail/profilesvc 0:91010 755

mkdir -p /jail/tmp
chmod a+rwxt /jail/tmp

mkdir -p /jail/dev
mknod /jail/dev/urandom c 1 9

cp -r zoobar /jail/
rm -rf /jail/zoobar/db

python /jail/zoobar/zoodb.py init-person
python /jail/zoobar/zoodb.py init-transfer
# For Cred DB
python /jail/zoobar/zoodb.py init-credential
# For bank DB
python /jail/zoobar/zoodb.py init-bank

# Change last 7 back to 0 when done. Used to be 50:55
set_perms 50:55 550 /jail/zoobar/db
set_perms 50:55 770 /jail/zoobar/db/person
set_perms 50:55 660 /jail/zoobar/db/person/person.db
set_perms 50:55 770 /jail/zoobar/db/transfer
set_perms 50:55 660 /jail/zoobar/db/transfer/transfer.db
# For Cred DB
set_perms 71010:71010 700 /jail/zoobar/db/cred
set_perms 71010:71010 600 /jail/zoobar/db/cred/cred.db
# For bank DB
set_perms 81010:81010 700 /jail/zoobar/db/bank
set_perms 81010:81010 600 /jail/zoobar/db/bank/bank.db

# Change last 7 back to 0 when done
set_perms 70:80 550 /jail/zoobar/media
set_perms 70:80 440 /jail/zoobar/media/lion_awake.jpg
set_perms 70:80 440 /jail/zoobar/media/lion_sleeping.jpg
set_perms 70:80 440 /jail/zoobar/media/zoobar.css

# set_perms 90:99 550 /jail/zoobar/*.py
# set_perms 90:99 550 /jail/zoobar/*.pyc

# set_perms 90:99 550 /jail/zoobar/auth_client.py
# set_perms 90:99 550 /jail/zoobar/auth.py
# set_perms 90:99 550 /jail/zoobar/auth.pyc
# set_perms 90:99 550 /jail/zoobar/auth-server.py
# set_perms 90:99 550 /jail/zoobar/bank.py
# set_perms 90:99 550 /jail/zoobar/bank.pyc
# set_perms 90:99 550 /jail/zoobar/bank-server.py
# set_perms 90:99 550 /jail/zoobar/debug.py
# set_perms 90:99 550 /jail/zoobar/debug.pyc
# set_perms 90:99 550 /jail/zoobar/echo.py
# set_perms 90:99 550 /jail/zoobar/echo.pyc
# set_perms 90:99 550 /jail/zoobar/echo-server.py
# set_perms 90:99 550 /jail/zoobar/index.py
# set_perms 90:99 550 /jail/zoobar/index.pyc
# set_perms 90:99 550 /jail/zoobar/__init__.py
# set_perms 90:99 550 /jail/zoobar/__init__.pyc
# set_perms 90:99 550 /jail/zoobar/login.py
# set_perms 90:99 550 /jail/zoobar/login.pyc
# set_perms 90:99 550 /jail/zoobar/pbkdf2.py
# set_perms 90:99 550 /jail/zoobar/profile.py
# set_perms 90:99 550 /jail/zoobar/profile.pyc
# set_perms 90:99 550 /jail/zoobar/profile-server.py
# set_perms 90:99 550 /jail/zoobar/rpclib.py
# set_perms 90:99 550 /jail/zoobar/rpclib.pyc
# set_perms 90:99 550 /jail/zoobar/sandboxlib.py
# set_perms 90:99 550 /jail/zoobar/transfer.py
# set_perms 90:99 550 /jail/zoobar/transfer.pyc
# set_perms 90:99 550 /jail/zoobar/users.py
# set_perms 90:99 550 /jail/zoobar/users.pyc
# set_perms 90:99 550 /jail/zoobar/zoobarjs.py
# set_perms 90:99 550 /jail/zoobar/zoobarjs.pyc
# set_perms 90:99 550 /jail/zoobar/zoodb.py
# set_perms 90:99 550 /jail/zoobar/zoodb.pyc

set_perms 90:99 555 /jail/zoobar/index.cgi
