<VirtualHost *:80>
  ServerName {server_name}

  DocumentRoot "{site_path}/html"

  <Directory "{site_path}/html">
    Options Indexes FollowSymLinks MultiViews
    AllowOverride All
    Order allow,deny
    Allow from all
  </Directory>
</VirtualHost>

