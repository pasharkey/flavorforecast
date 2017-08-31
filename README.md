# Flavor Forecast
An Amazon Alexa skill developed in Python which queries the flavor of the day information from The Dairy Godmother [flavor forecast calendar](http://www.thedairygodmother.com/flavor-of-the-day-forecast/). 

Certified and available on the Alexa skill storefront:
TBD

### Examples
    "Alexa, ask Flavor Forecast what the flavor forecast is today?"
    "Alexa, ask Flavor Forecast for the flavor of the day on August 21, 2017"
    "Alexa, ask Flavor Forecast is the The Dairy Godmother open?"
    

### Requirements
Uses [Zappa](https://github.com/Miserlou/Zappa) to deploy on AWS Lambda + API Gateway  

## Installation and Deployment
### Create a new virtualenv
```bash
mkvirtualenv --python=[path_to_python2] [env_name]
```
### Initialize and Deploy with Zappa
```bash 
zappa init
zappa deploy dev
```

### Contact
patrick.sharkey@gmail.com