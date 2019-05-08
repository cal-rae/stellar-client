# stellar-client
Package for querying data on [New Sun Road's](https://newsunroad.com) Stellar platform
# THIS PROJECT IS UNSUPPORTED BY NEW SUN ROAD AND COMPATIBILITY WITH THE CURRENT STELLAR API IS NOT GUARANTEED
 
## Installation
1. Clone the repository into your project directory `git clone https://github.com/cal-rae/stellar-client.git`
2. Build the package: `py -m pip install ./stellar-client`
3. Create a local file called `auth_config.py` and add your token to it in one line `stellar_token = '[your token]'`. See `auth_config_template.py` for an example.
4. See `example.py` for example usage (copied below).

## Example usage

```python
import datetime as dt
import pandas as pd

from auth_config import stellar_token as token
from stellar_client import StellarClient

# Set start and end times
t_start = dt.datetime(2018, 11, 14)
t_stop = dt.datetime(2018, 11, 15, 6)

# Set parameters that you want
parameters = 'batteryVoltage,batteryCurrent'

# Example parameters:
# ambientTemperature,dcBusVoltage,batteryVoltage,batteryStateOfCharge,
# batteryChargeEnergy,batteryDischargeEnergy,loadVoltage,lifetimeLoadEnergy,
# lifetimeMeteredLoadEnergy,lifetimeSolarEnergy,solarChargerVoltage,
# batteryPowerOut,solarPower,loadPower,meteredLoadPower

# Set the time resolution here
t_interval = '5-mins'

# Put the info to look up the system here
power_system = {
    'org': 'newsunroad',
    'site': 'pc_solstation_a'
}

# File to save - best to use the name 'out.csv' so you don't check in
save_to = 'out.csv'

# Get the data
client = StellarClient(
    system=power_system,
    parameters=parameters,
    t_interval=t_interval,
    token=token,
    save_to=save_to,
    batch_size_days=20
)

# Now you have a data frame to work with
df = client.get_data(t_start=t_start, t_stop=t_stop)

print(df)

# You can also re-load from the csv
df2 = pd.read_csv(save_to)

print(df2)

```
