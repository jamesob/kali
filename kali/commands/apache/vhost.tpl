<VirtualHost *:80>
  ServerName {server_name}

  DocumentRoot "{site_path}/html"

  #CustomLog "|/usr/local/sbin/cronolog {site_path}/logs/%Y/%m/access-%Y-%m-%d.log" combined
  #ErrorLog "|/usr/local/sbin/cronolog {site_path}/logs/%Y/%m/error-%Y-%m.log"
    
  <Directory "{site_path}/html">
    Options Indexes FollowSymLinks MultiViews
    AllowOverride All
    Order allow,deny
    Allow from all
  </Directory>
</VirtualHost>

