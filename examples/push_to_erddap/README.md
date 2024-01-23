# How to push data to an ERDDAP ([EDDTableFromHttpGet](https://coastwatch.pfeg.noaa.gov/erddap/download/setupDatasetsXml.html#EDDTableFromHttpGet))

## 1. Set up your tomcat server.

Your server must be configured for HTTPS in order to be able to "push" data records into it. In many production enviroments, tomcat runs behind a proxy (Apache or a hardware network device) which presents the necessary certificate chain to the client and handles the encryption of the external traffic. Our servers run this way. In this case, you just have to configure tomcat to respond with the correct information when ERDDAP asks about the host and protocol that was used to make the request. This configuration is added to the &lt;Connector&gt; tag in the Tomcat server.xml. It might look something like this (Tomcat 9):

               proxyName="public.pmel.noaa.gov" [this is the name of the host providing the proxy (Apache or a network device) to which clients will connect to push data to the ERDDAP]
               proxyPort="80"  [The port on which the proxy accepts connections, almost always 80]
               scheme="https"  [This is where you tell tomcat that incoming connections are using HTTPS via the proxy.]
               secure="true"   [This is where you tell tomcat the incoming connections are secured by the proxy.]

An ERDDAP running behind an proxy providing HTTPS configured in this way will accept incoming data to a properly configured data set.

## 2. Set up your "push" data set.

As with just about every ERDDAP dataset configuration, to make a "push" data set you start with an example data file and run GenerateDatasetsXml.sh to make the <dataset> configuration. The first line is a list of the variables, which must include 3 magic variables used by ERDDAP during the insert. The magic variables ("timestamp","author","command") must be in order at the end of the list.

Here's an example.
["platform_id","time","latitude","longitude","depth","fake","project","group","timestamp","author","command"]

And add a line of data to help ERDDAP figure out the data types (quotes for string, numbers don't have quotes and use decimal points for floats).

["sailboat001","2024-01-01T22:49:51Z",-9.562630589718495,69.31405830132954,3.1017628668307577,0.7170216267024074,"Test
with a Long Spacey Project Name","SDIG",1.704840591664E9,"Schweitzer",0]


Place this file in a directory for which the tomcat user running the ERDDAP has write permission. Name file with the value of the id column (sailboat001.jsonl in this example). There are infinite ways in which you can organize the incoming data and if you accepting data from multiple instruments on multiple platforms you might want to read the documentation, but for now let's assume a simple case where you identify where a where an observation came from by the value of some id column (platform_id in this case).

We will use that fact as part of our answers when we run GenerateDatasetsXml.sh, so run it and choose the *EDDTableFromHttpGet* as the data type.

After the directory name and file name (in this case you can leave it blank) you have to [identify which variables are "required"](https://coastwatch.pfeg.noaa.gov/erddap/download/setupDatasetsXml.html#httpGetRequiredVariables). In this example we'll say platform_id and time. Any observation can be uniquely identified by these two variables. The [directory structure](https://coastwatch.pfeg.noaa.gov/erddap/download/setupDatasetsXml.html#httpGetDirectoryStructure) tells ERDDAP how to organize the incoming data. In our case, the simplest answer that works is platform_id.

Tell ERDDAP who can post data with the [getKeys](https://coastwatch.pfeg.noaa.gov/erddap/download/setupDatasetsXml.html#httpGetKeys). I typically use lastname_PASSWORD. These keys are ostensibly secrets that you want to keep out of your github repo and not share.

If you know the structure of the data (in terms of the DSG type) you can go ahead and define the cdm_data_type, the data type variables (cdm_trajectory_variables, for example), and assign the appropriate variable the id cf_role.
