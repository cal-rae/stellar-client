import datetime as dt
import pandas as pd

from auth_config import stellar_token as token
from stellar_client import StellarClient

# Set start and end times
t_start = dt.datetime(2019, 5, 6)
t_stop = dt.datetime(2019, 5, 7)

# Set parameters that you want
parameters = 'meteredLoadEnergyUse,meteredLoadPower'

# Example parameters:
# meteredLoadPower,meteredLoadEnergyUse

# Set the time resolution here
t_interval = '5-mins'

# Put the info to look up the system here. Use the SolSense meter id as the
# site. Can select ...mtr1 through ...mtr9
power_system = {
    'org': 'newsunroad',
    'site': 'pc_solstation_a_mtr5'
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
print(df.mean())
