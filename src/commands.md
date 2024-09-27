# Steps:
1. Install mahimahi from source.
sudo apt-get install autotools-dev autoconf libtool apache2 apache2-dev protobuf-compiler libprotobuf-dev libssl-dev xcb libxcb-composite0-dev libxcb-present-dev libcairo2-dev libpango1.0-dev gnuplot

mkdir -p $HOME/opt
cd $HOME/opt
git clone git@github.com:ravinet/mahimahi.git
./autogen.sh
./configure
make
sudo make install

sudo sysctl -w net.ipv4.ip_forward=1

2. Install iperf3
sudo apt install iperf3

3. Clone and install ccas (rocc_ccmatic, rocc_kernel, simple_rocc)
sudo modprobe tcp_bbr

4. Copy mahimahi-traces

5. Setup ramdisk (for mm logs)
sudo mkdir /mnt/ramdisk
sudo mount -t tmpfs -o size=10G tmpfs /mnt/ramdisk