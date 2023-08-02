param(
	[Parameter(ValueFromPipeline=$true)]$CertFolder = "C:\workspace\win-acme\certs",
	$LoginCertFolder = "C:\workspace\wings\git\wings\conf"
)

# this script is run by win-acme-simple to update the login server's cert files
# service restart not needed, login service reads the cert on each connect
#$loginService = "TopazConnect"

#stop-service $loginService

dir $CertFolder | ? name -like game.* | copy-item -Destination $LoginCertFolder
dir $CertFolder | ? name -like game.* | copy-item -Destination $LoginCertFolder\..\..\..\runtime\wings\conf

#start-service $loginService
