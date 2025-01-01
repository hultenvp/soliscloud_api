# soliscloud-api
Python implementation for the SolisCloud API

Supports all endpoints specified in SolisCloud API v1.2 for reading Solis PV monitoring data from the SolisCloud service.

# Prerequisites
Usage of the API requires an active account on https://www.soliscloud.com and also requires an API key and secret, 
to be obtained via SolisCloud.

# Supported endpoints

* /V1/API/STATIONYEAR (PLANT YEARLY GRAPH)
* /V1/API/STATIONALL (PLANT CUMULATIVE GRAPH)
* /V1/API/INVERTERDAY (INVERTER DAILY GRAPH)
* /V1/API/INVERTERMONTH (INVERTER MONTHLY GRAPH)
* /V1/API/INVERTERYEAR (INVERTER YEARLY GRAPH)
* /V1/API/INVERTERALL (INVERTER CUMULATIVE GRAPH)
* /V1/API/ALARMLIST (ALARM INFO CHECK)
* /V1/API/STATIONDETAILLIST (BATCH ACQUIRE PLANT DETAILS)
* /V1/API/INVERTERDETAILLIST (BATCH ACQUIRE INVERTER DETAILS)
* /V1/API/STATIONDAYENERGYLIST (BATCH ACQUIRE PLANT DAILY GENERATION)
* /V1/API/STATIONMONTHENERGYLIST (BATCH ACQUIRE PLANT MONTHLY GENERATION)
* /V1/API/STATIONYEARENERGYLIST (BATCH ACQUIRE PLANT YEARLY GENERATION)
* /V1/API/EPMLIST (EPM LIST)
* /V1/API/EPMDETAIL (EPM DETAILS)
* /V1/API/EPM/DAY (EPM DAILY GRAPH)
* /V1/API/EPM/MONTH (EPM MONTHLY GRAPH)
* /V1/API/EPM/YEAR (EPM YEARLY GRAPH)
* /V1/API/EPM/ALL (EPM CUMULATIVE GRAPH)

# Known issues

1. If the local time deviates more than 15 minutes from SolisCloud server time then the server will respond with HTTP 408.
2. When calls to the API return with error message "数据异常 请联系管理员" (English: abnormal data, please contact administrator), then SolisCloud helpdesk needs to fix your account, raise a ticket via soliscloud.com
3. I could not test the use of the NMI parameter for AUS use cases, please create a ticket or pull request if you experience issues
