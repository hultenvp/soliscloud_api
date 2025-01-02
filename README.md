# soliscloud-api
Python implementation for the SolisCloud API

Supports all endpoints specified in SolisCloud API spec 2.0 for reading Solis PV monitoring data from the SolisCloud service.

# Prerequisites
Usage of the API requires an active account on https://www.soliscloud.com and also requires an API key and secret, 
to be obtained via SolisCloud.

* Submit a [service ticket](https://solis-service.solisinverters.com/support/solutions/articles/44002212561-api-access-soliscloud) and wait till it is resolved.
* Go to https://www.soliscloud.com/#/apiManage.
* Activate API management and agree with the usage conditions.
* After activation, click on view key tot get a pop-up window asking for the verification code.
* First click on "Verification code" after which you get an image with 2 puzzle pieces, which you need to overlap each other using the slider below.
* After that, you will receive an email with the verification code you need to enter (within 60 seconds).
* Once confirmed, you get the API ID, secret and API URL


# Supported API calls
NOTE: The spec uses the terms Plant, Station and Power Station interchangeably. In this document we will use plant.

| Call                             | Description |
|----------------------------------|---------------------------------------------------------------|
| /v1/api/inverterList             | Obtain list of all inverters under account or a specific plant. |
| /v1/api/inverterDetail           | Obtain details for a single inverter. |
| /v1/api/inverterDetailList       | Obtain list of details of all inverters under account. |
| /v1/api/inverterDay              | Obtain real-time data of a single inverter on the specified day. |
| /v1/api/inverterMonth            | Obtain daily data of a single inverter for the specified month. |
| /v1/api/inverterYear             | Obtain monthly data of a single inverter for the specified year. |
| /v1/api/inverterAll              | Obtain cumulative data of a single inverter for the current year. |
| /v1/api/inverter/shelfTime :new: | Warranty data of a single inverter. |
| /v1/api/alarmList                | Obtain device alarm list of all or specific inverter under account. |
| /v1/api/collectorList            | Obtain list of all collectors under account or for a specific plant. |
| /v1/api/collectorDetail          | Obtain details for a single collector. |
| /v1/api/collector/day :new:      | Obtain daily data for a single collector. |
| /v1/api/epmList                  | Obtain list of all EPM's under account or for a specific plant. |
| /v1/api/epmDetail                | Obtain details for a single EPM. |
| /v1/api/epm/day                  | Obtain real-time data of a single EPM on the specified day. |
| /v1/api/epm/month                | Obtain daily data of a single EPM for the specified month. |
| /v1/api/epm/year                 | Obtain monthly data of a single EPM for the specified year. |
| /v1/api/epm/all                  | Obtain cumulative data of a single EPM for the current year. |
| /v1/api/weatherList :new:        | Obtain list of all meteorological instruments under account or for a specific plant. |
| /v1/api/weatherDetail :new:      | Obtain details for a single meteorological instrument. |
| /v1/api/userStationList          | Obtain list of all plants under account. |
| /v1/api/stationDetail            | Obtain details for a single plant. |
| /v1/api/stationDetailList        | Obtain details for a all plants under account. |
| /v1/api/stationDayEnergyList     | Obtain real-time data of a single or all plants on the specified day. |
| /v1/api/stationMonthEnergyList   | Obtain daily data of a single or all plants for the specified month. |
| /v1/api/stationYearEnergyList    | Obtain monthly data of a single or all plants for the specified year. |
| /v1/api/stationDay               | Obtain real-time data of a single plant on the specified day. |
| /v1/api/stationMonth             | Obtain daily data of a single plant for the specified month. |
| /v1/api/stationYear              | Obtain monthly data of a single plant for the specified year. |
| /v1/api/stationAll               | Obtain cumulative data of a single plant for the current year. |

# Currently unsupported API calls 
| Call                             | Description |
|----------------------------------|---------------------------------------------------------------|
| /v1/api/addStation               | Add a plant to the account. |
| /v1/api/stationUpdate            | Update plant information. |
| /v1/api/addStationBindCollector  | Binding a new collector to the plant. |
| /v1/api/delCollector             | Unbind a collector from the plant. |
| /v1/api/addDevice                | Binding a new inverter to the plant. |

# Known issues

1. If the local time deviates more than 15 minutes from SolisCloud server time then the server will respond with HTTP 408.
2. When calls to the API return with error message "数据异常 请联系管理员" (English: abnormal data, please contact administrator.), then SolisCloud helpdesk needs to fix your account, raise a ticket via soliscloud.com
3. I could not test the use of the NMI parameter for AUS use cases, please create a ticket or pull request if you experience issues
