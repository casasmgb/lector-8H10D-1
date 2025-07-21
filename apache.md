## En Debian

```
sudo vim /etc/apache2/sites-available/000-default.conf
```

agregar

```
    # Proxy WebSocket connections
    RewriteEngine On
    RewriteCond %{HTTP:Upgrade} websocket [NC]
    RewriteCond %{HTTP:Connection} upgrade [NC]
    RewriteRule ^/?(.*) ws://localhost:8765/$1 [P,L]
```

habilitar y reiniciar

```
sudo a2enmod proxy proxy_wstunnel rewrite
sudo systemctl restart apache2
```
