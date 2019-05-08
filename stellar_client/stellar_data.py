import json
import pytz
import warnings
import logging

import pandas as pd
import requests
import datetime as dt

logger = logging.getLogger(__name__)


class StellarData:
    """
    Get data from Stellar API. Set the authentication in my_auth_config.py
    """

    def __init__(self,
                 system: dict,
                 parameters: str,
                 t_interval: str,
                 save_to: str,
                 token: str,
                 batch_size_days=20):
        """
        Makes a call to Stellar API
        :param system: dict, this is the power_system dictionary as returned by INI config
        :param parameters: str, see the API documentation for available parameters:
        ex: 'batteryChargePower,solarPower,loadPower'. If it's not available returns empty
        :param t_interval: str, the resolution of the call.
        ex: '1-mins', '5-mins'
        :param save_to: str, file path to save to. If you don't want to save pass ''
        :param batch_size_days: int, the number of days to get at once. Too many days results in timeout
        :param token: str, the stellar token
        :return: relevant data (pd.DataFrame)
        """

        self.system = system
        self.parameters = parameters
        self.token = token
        self.t_interval = t_interval
        self.save_to = save_to
        self.batch_size_days = batch_size_days

        self._get_cookies()

    def _get_cookies(self):
        """Get the cookies by setting the organization
        """
        post_url = 'https://stellar.newsunroad.com/api/v0/setOrganization/{}'.format(self.system['org'])

        post_r = requests.post(post_url,
                               headers={'Authorization': 'token ' + self.token}
                               )

        self._my_cookies = post_r.cookies.get_dict()

    @staticmethod
    def to_pandas_dataframe(d_dict):
        """Convert the dictionary into a dataframe"""
        files = pd.DataFrame.from_dict(d_dict, orient='columns')
        if files.empty:
            return files
        files['time'] = pd.to_datetime(files.time, infer_datetime_format=True)
        files.set_index(pd.DatetimeIndex(files['time']), inplace=True)
        logger.info('Data received')
        return files

    @staticmethod
    def parse_response(response, d_dict):
        """Parse the response from the HTTP request"""
        try:
            if response.status_code == 200:
                response_json = response.json()
                for entry in response_json['data']:
                    for rel_dict in entry['timeSeries']:
                        for key in rel_dict.keys():
                            if key in d_dict.keys():
                                d_dict[key].append(rel_dict[key])
                            else:
                                d_dict[key] = [rel_dict[key]]
                return d_dict

            else:
                warnings.warn(response.text)
                raise ValueError("Check the power system name you entered and if the API changed")
        except json.decoder.JSONDecodeError:
            warnings.warn('JSONDecodeError')

    def get_data(self, t_start: dt.datetime, t_stop: dt.datetime):
        """
        Make an API call with the start and end times
        :param t_start: dt.datetime, time to start the data
        :param t_stop: dt.datetime, time to stop the data call
        :return:
        """
        # Call parameters
        logger.debug('getting data for {} for {} to {}'.format(self.system["site"], t_start, t_stop))
        data_dict = dict()
        while t_start < t_stop:
            if t_start + dt.timedelta(days=self.batch_size_days) < t_stop:
                t_end = (t_start + dt.timedelta(days=self.batch_size_days))
            else:
                t_end = t_stop
            logger.debug('{} - {}'.format(t_start, t_end))
            t_start_str = t_start.strftime('%Y-%m-%dT%H:%M:%SZ')
            t_end_str = t_end.strftime('%Y-%m-%dT%H:%M:%SZ')

            url = 'https://stellar.newsunroad.com/api/v0/ts/' + self.system['site'] + '?start=' + t_start_str + \
                  '&end=' + t_end_str + '&binDuration=' + self.t_interval + '&params=' + self.parameters

            resp = requests.get(url,
                                cookies=self._my_cookies,
                                headers={'Authorization': 'token ' + self.token}
                                )
            data_dict = self.parse_response(resp, data_dict)
            t_start = t_end

        final_df = self.to_pandas_dataframe(d_dict=data_dict)

        if self.save_to:
            self.save_data(final_df, self.save_to)

        return final_df

    def save_data(self, df, file):
        """Save to csv"""

        def to_utc(data):
            """Make sure it's UTC"""
            if data.empty:
                return data
            data.index = data.index.tz_localize(pytz.utc)
            return data

        df = to_utc(df)
        filename = file.format(self.system['site'])
        with open(filename, 'w') as f:
            df.to_csv(f, header=True)
            f.close()
        logger.debug('saved stellar api data to: {}'.format(filename))
