# soliscloud-api
Python implementation for the SolisCloud API

Supports all endpoints specified in SolisCloud API v1.2 for reading Solis PV monintoring data from the SolisCloud service.

# Prerequisites
Usage of the API requires an active account on https://www.soliscloud.com and also requires an API key and secret, 
to be obtained via SolisCloud.

# Supported endpoints

* /V1/API/STATIONYEAR (Plant yearly graph)
* /V1/API/STATIONALL (Plant cumulative graph)
* /V1/API/INVERTERDAY (Inverter daily graph)
* /V1/API/INVERTERMONTH (Inverter monthly graph)
* /V1/API/INVERTERYEAR (Inverter yearly graph)
* /V1/API/INVERTERALL (Inverter cumulative graph)
* /V1/API/ALARMLIST (Alarm info check)
* /V1/API/STATIONDETAILLIST (Batch acquire plant details)
* /V1/API/INVERTERDETAILLIST (Batch acquire inverter details)
* /V1/API/STATIONDAYENERGYLIST (Batch acquire plant daily generation)
* /V1/API/STATIONMONTHENERGYLIST (Batch acquire plant monthly generation)
* /V1/API/STATIONYEARENERGYLIST (Batch acquire plant yearly generation)
* /V1/API/EPMLIST (EPM List)
* /V1/API/EPMDETAIL (EPM Details)
* /V1/API/EPM/DAY (EPM daily graph)
* /V1/API/EPM/MONTH (EPM monthly graph)
* /V1/API/EPM/YEAR (EPM yearly graph)
* /V1/API/EPM/ALL (EPM cumulative graph)

# Known issues

1. If the local time deviates more than 15 minutes from SolisCloud server time then the server will respond with HTTP 408.
2. When calls to the API return with error message "数据异常 请联系管理员" (English: abnormal data, please contact administrator), then SolisCLoud helpdesk needs to fix your account, raise a ticket via soliscloud.com
