# How to push data to an ERDDAP (EDDTableFromHttpGet)

## 1. Set up your tomcat server.

Your server must be configured for HTTPS in order to be able to "push" data records into it. In many production enviroments, tomcat runs behind a proxy (Apache or a hardware network device) which presents the necessary certificate chain to the client and handles the encryption of the external traffic. Our servers run this way. In this case, you must also configure tomcat to respond with the correct information when ERDDAP asks about the host and protocal used to make the request. This configuration is added to the <Connector> tag in the Tomcat server.xml. It might look something like this (Tomcat 9):

               proxyName="public.pmel.noaa.gov" [this is the name of the host providing the proxy (Apache or a network device) to which clients will connect to push data to the ERDDAP]
               proxyPort="80"  [The port on which the proxy accepts connections, almost always 80]
               scheme="https"  [This is where you tell tomcat that incoming connections are using HTTPS via the proxy.]
               secure="true"   [This is where you tell tomcat the incoming connections are secured by the proxy.]

An ERDDAP running behind an proxy providing HTTPS configured in this way will accept incoming data to a properly configured data set.

## 2. Set up your "push" data set.

