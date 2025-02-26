# myems-admin

## Introduction

系统管理用户界面，用于MyEMS系统配置

Admin UI for MyEMS system settings

## Prerequisites

nginx-1.18.0 or later


## Installation

### Option 1: Install myems-admin on Docker

In this section, you will install myems-admin on Docker.

* Copy source code to root directory

On Windows:
```bash
cp -r myems/myems-admin c:\
cd c:\myems-admin
```

On Linux:
```bash
cp -r myems/myems-admin /
cd /myems-admin
```

* Manually replace ~~127.0.0.1:8000~~ in nginx.conf with actual **HOST** ip and port of myems-api
```bash
nano nginx.conf
```

```bash
      proxy_pass http://127.0.0.1:8000/;
```

* Build a Docker image

```bash
docker build -t myems/myems-admin .
```

To build for multiple platforms and not only for the architecture and operating system that the user invoking the build happens to run.
You can use buildx and set the --platform flag to specify the target platform for the build output, (for example, linux/amd64, linux/arm64, or darwin/amd64).
```bash
docker buildx build --platform=linux/amd64 -t myems/myems-admin .
```


* Run a Docker container

If run on Windows host, bind-mount a share upload file folder at c:\myems-upload to the container and also bind-mount nginx.conf 
-v parameter for upload folder must be same with that in myems-api
```bash
docker run -d -p 8001:8001 -v c:\myems-upload:/var/www/myems-admin/upload -v c:\myems-admin/nginx.conf:/etc/nginx/nginx.conf:ro --log-opt max-size=1m --log-opt max-file=2 --restart always --name myems-admin myems/myems-admin
```

If run on Linux host, bind-mount a share upload file folder at /myems-upload to the container and also bind-mount nginx.conf 
```bash
docker run -d -p 8001:8001 -v /myems-upload:/var/www/myems-admin/upload -v /myems-admin/nginx.conf:/etc/nginx/nginx.conf:ro --log-opt max-size=1m --log-opt max-file=2 --restart always --name myems-admin myems/myems-admin
```

* -d Run container in background and print container ID

* -p Publish a container's port(s) to the host, 8001:8001 (Host:Container) binds port 8001 (right)  of the container to 
TCP port 8001 (left) of the host machine.

* -v If you use -v or --volume to bind-mount a file or directory that does not yet exist on the Docker host, 
-v creates the endpoint for you. It is always created as a directory.
The ro option, if present, causes the bind mount to be mounted into the container as read-only.

* --log-opt max-size=2m The maximum size of the log before it is rolled. A positive integer plus a modifier representing the unit of measure (k, m, or g).

* --log-opt max-file=2 The maximum number of log files that can be present. If rolling the logs creates excess files, the oldest file is removed. A positive integer. 

* --restart Restart policy to apply when a container exits

* --name Assign a name to the container

If you want to immigrate the image to another computer,
* Export image to tarball file
```bash
docker save --output myems-admin.tar myems/myems-admin
```

* Copy the tarball file to another computer, and then load image from tarball file
```bash
docker load --input .\myems-admin.tar
```

## Option 2: Install on NGINX Server

* Install NGINX Server

refer to http://nginx.org/en/docs/install.html

* Configure NGINX
```bash
sudo nano /etc/nginx/nginx.conf
```
In the 'http' section, add some directives:
```
http{
    client_header_timeout 600;
    client_max_body_size 512M;
    gzip on;
    gzip_min_length 512;
    gzip_proxied any;
    gzip_types *;
    gzip_vary on;
    proxy_buffering off;
    ...

}
```

Add a new 'server' section with directives as below:
```
  server {
      listen                 8001;
      server_name     myems-admin;
      location / {
          root    /var/www/myems-admin;
          index index.html index.htm;
      }
      ## To avoid CORS issue, use Nginx to proxy myems-api to path /api 
      ## Add another location /api in 'server' and replace demo address http://127.0.0.1:8000/ with actual url
      location /api {
          proxy_pass http://127.0.0.1:8000/;
          proxy_connect_timeout 75;
          proxy_read_timeout 600;
          send_timeout 600;
      }
  }
```

* Install myems-admin :
  If the server can not connect to the internet, please compress the myems/myems-admin folder and upload it to the server and extract it to ~/myems/myems-admin
```bash
sudo mkdir /var/www
sudo cp -r myems/myems-admin  /var/www/myems-admin
sudo chmod 0755 -R /var/www/myems-admin
```
  Check the config file and change it if necessary:
```bash
sudo nano /var/www/myems-admin/app/api.js
```

## NOTE:
The 'upload' folder is for user uploaded files. DO NOT delete/move/overwrite the 'upload' folder when you upgraded myems-admin.
```bash
 /var/www/myems-admin/upload
```


## Option 3: Install on Apache2 Server
* Install Apache2 Server

refer to https://httpd.apache.org/docs/2.4/install.html

* Configure Apache2
```bash
  sudo vi /etc/apache2/ports.conf
```
Add a Listen
```
Listen 8001
```
```bash
sudo vi /etc/apache2/sites-available/000-default.conf
```
Add a new 'VirtualHost' as below
```
<VirtualHost 127.0.0.1:8001>
        ServerAdmin MyEMS-admin
        DocumentRoot /var/www/myems-admin
        
        <Directory "var/www/myems-admin">
                Options FollowSymLinks
                AllowOverride All
                Require all granted
    			Header set Access-Control-Allow-Origin *
        </Directory>
        ErrorLog ${APACHE_LOG_DIR}/error.log
        CustomLog ${APACHE_LOG_DIR}/access.log combined
        ProxyRequests Off
		ProxyPreserveHost On
		
		<Proxy *>
			Order Deny,Allow
			Allow from all
		</Proxy>
		ProxyPass /api http://127.0.0.1:8000/
		ProxyPassReverse /api http://127.0.0.1:8000/
</VirtualHost>
```

* Install myems-admin :
  If the server can not connect to the internet, please compress the myems/myems-admin folder and upload it to the server and extract it to ~/myems/myems-admin
```bash
sudo cp -r myems/myems-admin  /var/www/myems-admin
sudo chmod 0755 -R /var/www/myems-admin
```
  Check the config file and change it if necessary:
```bash
sudo nano /var/www/myems-admin/app/api.js
```


## References

[1].  https://myems.io

[2].  https://dev.mysql.com/doc/connector-python/en/ 

[3]. https://nginx.org/