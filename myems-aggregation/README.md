## myems-aggregation

Data Aggregation Service 

数据汇总服务

## Introduction

This service is a component of MyEMS to aggregate normalized data up to multiple dimensions.

## Prerequisites

mysql-connector-python

python-decouple


## Quick Run for Development

```bash
cd myems/myems-aggregation
pip install -r requirements.txt
cp example.env .env
chmod +x run.sh
./run.sh
```

## Installation

### Option 1: Install myems-aggregation on Docker

In this section, you will install myems-aggregation on Docker.

* Copy source code to root directory

On Windows:
```bash
cp -r myems/myems-aggregation c:\
cd c:\myems-aggregation
```

On Linux:
```bash
cp -r myems/myems-aggregation /
cd /myems-aggregation
```

* Create .env file based on example.env file

Manually replace ~~127.0.0.1~~ with real **HOST** IP address.

```bash
cp example.env .env
```

* Build a Docker image

```bash
docker build -t myems/myems-aggregation .
```

To build for multiple platforms and not only for the architecture and operating system that the user invoking the build happens to run.
You can use buildx and set the --platform flag to specify the target platform for the build output, (for example, linux/amd64, linux/arm64, or darwin/amd64).
```bash
docker buildx build --platform=linux/amd64 -t myems/myems-aggregation .
```

* Run a Docker container on Linux (run as superuser)
```bash
docker run -d -v /myems-aggregation/.env:/code/.env:ro --log-opt max-size=1m --log-opt max-file=2 --restart always --name myems-aggregation myems/myems-aggregation
```

* Run a Docker container on Windows (Run as Administrator)
```bash
docker run -d -v c:\myems-aggregation\.env:/code/.env:ro --log-opt max-size=1m --log-opt max-file=2 --restart always --name myems-aggregation myems/myems-aggregation
```

* -d Run container in background and print container ID

* -v If you use -v or --volume to bind-mount a file or directory that does not yet exist on the Docker host, 
-v creates the endpoint for you. It is always created as a directory.
The ro option, if present, causes the bind mount to be mounted into the container as read-only.

* --log-opt max-size=2m The maximum size of the log before it is rolled. A positive integer plus a modifier representing the unit of measure (k, m, or g).

* --log-opt max-file=2 The maximum number of log files that can be present. If rolling the logs creates excess files, the oldest file is removed. A positive integer. 

* --restart Restart policy to apply when a container exits

* --name Assign a name to the container

The absolute path before colon is for path on host  and that may vary on your system.
The absolute path after colon is for path on container and that CANNOT be changed.
By passing .env as bind-mount parameter, you can change the configuration values later.
If you changed .env file, restart the container to make the change effective.

* Immigrate the Docker container

* Export image to tarball file
```bash
docker save --output myems-aggregation.tar myems/myems-aggregation
```
* Copy the tarball file to another computer, and then load image from tarball file
```bash
docker load --input .\myems-aggregation.tar
```

### Option 2: Online install myems-aggregation on Ubuntu Server with internet access

In this section, you will install myems-aggregation on Ubuntu Server with internet access.

```bash
cp -r myems/myems-aggregation /myems-aggregation
cd /myems-aggregation
pip install -r requirements.txt
```
Copy exmaple.env file to .env and modify the .env file:
```bash
cp /myems-aggregation/example.env /myems-aggregation/.env
nano /myems-aggregation/.env
```
Setup systemd service:
```bash
cp myems-aggregation.service /lib/systemd/system/
```
Enable the service:
```bash
systemctl enable myems-aggregation.service
```
Start the service:
```bash
systemctl start myems-aggregation.service
```
Monitor the service:
```bash
systemctl status myems-aggregation.service
```
View the log:
```bash
cat /myems-aggregation.log
```

### Option 3: Offline install myems-aggregation on Ubuntu Server without internet access

In this section, you will install myems-aggregation on Ubuntu Server without internet access.

Download on any server with internet access:
```bash
cd ~/tools
wget https://cdn.mysql.com//Downloads/Connector-Python/mysql-connector-python-8.0.28.tar.gz
git clone https://github.com/henriquebastos/python-decouple.git
cd ~
git clone https://github.com/MyEMS/myems.git
```

Copy files to the server without internet access and install prerequisites:
```bash
cd ~/tools
tar xzf mysql-connector-python-8.0.28.tar.gz
cd ~/tools/mysql-connector-python-8.0.28
python3 setup.py install
cd ~/tools/python-decouple
python3 setup.py  install
```

Install myems-aggregation service:
```bash
cp -r myems/myems-aggregation /myems-aggregation
cd /myems-aggregation
```
Copy exmaple.env file to .env and modify the .env file:
```bash
cp /myems-aggregation/example.env /myems-aggregation/.env
nano /myems-aggregation/.env
```
Setup systemd service:
```bash
cp myems-aggregation.service /lib/systemd/system/
```
Enable the service:
```bash
systemctl enable myems-aggregation.service
```
Start the service:
```bash
systemctl start myems-aggregation.service
```
Monitor the service:
```bash
systemctl status myems-aggregation.service
```
View the log:
```bash
cat /myems-aggregation.log
```

### References

[1]. https://myems.io

[2]. https://dev.mysql.com/doc/connector-python/en/

[3]. https://github.com/henriquebastos/python-decouple/
