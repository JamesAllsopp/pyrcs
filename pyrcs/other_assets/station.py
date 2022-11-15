"""Collect `railway station data <http://www.railwaycodes.org.uk/stations/station0.shtm>`_."""

import os
import re
import string
import urllib.parse

import bs4
import pandas as pd
import requests
from pyhelpers.dirs import cd
from pyhelpers.ops import fake_requests_headers
from pyhelpers.store import load_data

from ..parser import get_catalogue, get_last_updated_date, parse_tr
from ..utils import cd_data, collect_in_fetch_verbose, format_err_msg, home_page_url, init_data_dir, \
    is_home_connectable, print_conn_err, print_inst_conn_err, print_void_msg, save_data_to_file, \
    validate_initial


class Stations:
    """A class for collecting `railway station data`_.

    .. _`railway station data`: http://www.railwaycodes.org.uk/stations/station0.shtm
    """

    #: Name of the data
    NAME = 'Railway station data'
    #: Key of the `dict <https://docs.python.org/3/library/stdtypes.html#dict>`_-type data
    KEY = 'Stations'

    #: Key of the dict-type data of '*Mileages, operators and grid coordinates*'
    KEY_TO_STN = 'Mileages, operators and grid coordinates'

    #: URL of the main web page of the data
    URL = urllib.parse.urljoin(home_page_url(), '/stations/station0.shtm')

    #: Key of the data of the last updated date
    KEY_TO_LAST_UPDATED_DATE = 'Last updated date'

    def __init__(self, data_dir=None, update=False, verbose=True):
        """
        :param data_dir: name of data directory, defaults to ``None``
        :type data_dir: str or None
        :param update: whether to do an update check (for the package data), defaults to ``False``
        :type update: bool
        :param verbose: whether to print relevant information in console, defaults to ``True``
        :type verbose: bool or int

        :ivar dict catalogue: catalogue of the data
        :ivar str last_updated_date: last updated date
        :ivar str data_dir: path to the data directory
        :ivar str current_data_dir: path to the current data directory

        **Examples**::

            >>> from pyrcs.other_assets import Stations

            >>> stn = Stations()

            >>> stn.NAME
            'Railway station data'

            >>> stn.URL
            'http://www.railwaycodes.org.uk/stations/station0.shtm'
        """

        print_conn_err(verbose=verbose)

        self.catalogue = self.get_catalogue(update=update, verbose=False)

        self.last_updated_date = get_last_updated_date(url=self.URL, parsed=True, as_date_type=False)

        self.data_dir, self.current_data_dir = init_data_dir(self, data_dir, category="other-assets")

    def get_catalogue(self, update=False, verbose=False):
        """
        Get catalogue of railway station data.

        :param update: whether to do an update check (for the package data), defaults to ``False``
        :type update: bool
        :param verbose: whether to print relevant information in console, defaults to ``False``
        :type verbose: bool or int
        :return: catalogue of railway station data
        :rtype: dict

        **Examples**::

            >>> from pyrcs.other_assets import Stations  # from pyrcs import Stations

            >>> stn = Stations()

            >>> stn_data_cat = stn.get_catalogue()
            >>> type(stn_data_cat)
            dict
            >>> list(stn_data_cat.keys())
            ['Mileages, operators and grid coordinates',
             'Bilingual names',
             'Sponsored signs',
             'Not served by SFO',
             'International',
             'Trivia',
             'Access rights',
             'Barrier error codes',
             'London Underground',
             'Railnet']
        """

        data_name = urllib.parse.urlparse(self.URL).path.lstrip('/').rstrip('.shtm').replace('/', '-')
        ext = ".json"
        path_to_cat = cd_data("catalogue", data_name + ext)

        if os.path.isfile(path_to_cat) and not update:
            catalogue = load_data(path_to_cat)

        else:
            if verbose == 2:
                print("Collecting the catalogue of {}".format(self.NAME.lower()), end=" ... ")

            catalogue = None

            try:
                source = requests.get(url=self.URL, headers=fake_requests_headers())

            except Exception as e:
                if verbose == 2:
                    print("Failed. ", end="")
                print_inst_conn_err(update=update, verbose=verbose, e=e)

            else:
                try:
                    soup = bs4.BeautifulSoup(markup=source.text, features='html.parser')

                    cold_soup = soup.find_all('nav')[1]

                    hot_soup = {
                        a.text: urllib.parse.urljoin(self.URL, a.get('href'))
                        for a in cold_soup.find_all('a')}

                    catalogue = {}
                    for k, v in hot_soup.items():
                        sub_cat = get_catalogue(
                            v, update=True, confirmation_required=False, json_it=False)

                        if sub_cat != hot_soup:
                            if k in sub_cat.keys():
                                sub_cat.pop(k)
                            elif 'Introduction' in sub_cat.keys():
                                sub_cat.pop('Introduction')
                            if v in sub_cat.values():
                                catalogue[k] = sub_cat
                            else:
                                catalogue[k] = {'Introduction': v, **sub_cat}

                        else:
                            catalogue.update({k: v})

                    if verbose == 2:
                        print("Done.")

                    save_data_to_file(
                        self, data=catalogue, data_name=data_name, ext=ext,
                        dump_dir=cd_data("catalogue"), verbose=verbose, indent=4)

                except Exception as e:
                    print(f"Failed. {format_err_msg(e)}")

        return catalogue

    def _cdd(self, *sub_dir, **kwargs):
        """
        Change directory to package data directory and subdirectories (and/or a file).

        The directory for this module: ``"data\\other-assets\\stations"``.

        :param sub_dir: subdirectory or subdirectories (and/or a file)
        :type sub_dir: str
        :param kwargs: [optional] parameters of the function `pyhelpers.dir.cd`_
        :return: path to the backup data directory for the class
            :py:class:`~pyrcs.other_assets.station.Stations`
        :rtype: str

        .. _`pyhelpers.dir.cd`:
            https://pyhelpers.readthedocs.io/en/latest/_generated/pyhelpers.dir.cd.html
        """

        path = cd(self.data_dir, *sub_dir, mkdir=True, **kwargs)

        return path

    @staticmethod
    def check_row_spans(dat):
        """
        Check data where there are row spans.

        :param dat: preprocessed data of the station locations
        :type dat: pandas.DataFrame
        :return: data with row spans (if any)
        :rtype: pandas.DataFrame
        """

        temp0 = dat['Degrees Longitude'].str.split(' / ')
        temp1 = dat[temp0.map(len).map(lambda x: True if x > 1 else False)]

        cols = ['ELR', 'Mileage', 'Degrees Longitude', 'Degrees Latitude', 'Grid Reference']
        cols_ = [x for x in temp1.columns if x not in cols]

        temp_dat = []
        for col in cols:
            # noinspection PyUnresolvedReferences
            temp2 = temp1[col].map(lambda x: x.split(' / '))

            if cols.index(col) == 0:
                # noinspection PyTypeChecker
                temp_dat_ = temp1[cols_].join(temp2).explode(col)
                temp_dat_.index = range(len(temp_dat_))
            else:
                temp_dat_ = temp2.explode(col).to_frame()

            temp_dat.append(temp_dat_)

        temp_data = pd.concat(temp_dat, axis=1)
        temp_data = temp_data[dat.columns.to_list()]

        dat = pd.concat([dat.drop(index=temp1.index), temp_data], axis=0, ignore_index=True)

        dat.sort_values(['Station'], ignore_index=True, inplace=True)

        return dat

    @staticmethod
    def parse_coordinates_columns(dat):
        """
        Parse ``'Degrees Longitude'`` and ``'Degrees Latitude'`` of the station locations data.

        :param dat: preprocessed data of the station locations
        :type dat: pandas.DataFrame
        :return: data with parsed coordinates
        :rtype: pandas.DataFrame
        """

        ll_col_names = ['Degrees Longitude', 'Degrees Latitude']

        dat[ll_col_names] = dat[ll_col_names].applymap(
            lambda x: None if x.strip() == '' else float(re.sub(r'(c\.)|≈', '', x)))

        return dat

    @staticmethod
    def parse_station_column(dat):
        """
        Parse ``'Station'`` of the station locations data.

        :param dat: preprocessed data of the station locations
        :type dat: pandas.DataFrame
        :return: data with parsed station names and their corresponding CRS
        :rtype: pandas.DataFrame

        **Tests**::

            x = 'Hythe Road\t\t / [CRS awaited]'
            x = 'Heathrow Junction [sometimes referred to as Heathrow Interchange]\t\t / [no CRS?]'
        """

        temp1 = dat['Station'].str.split('\t\t', expand=True)
        temp1.columns = ['Station', 'CRS']
        dat['Station'] = temp1['Station']

        # Get notes for stations
        stn_note_ = pd.Series('', index=dat.index)
        for i, x in enumerate(temp1['Station']):
            if '[' in x and ']':
                y = re.search(r' \[(.*)]', x).group(0)  # Station Note
                dat.loc[i, 'Station'] = x.replace(y, '')
                stn_note_[i] = y.strip(' []')

        dat.insert(loc=dat.columns.get_loc('Station') + 1, column='Station Note', value=stn_note_)

        temp2 = temp1['CRS'].str.replace(' / /', ' &&& ').str.split(' / ', expand=True).fillna('')

        if temp2.shape[1] == 1:
            temp2.columns = ['CRS']
            temp2 = pd.concat([temp2, pd.DataFrame('', index=temp2.index, columns=['CRS Note'])], axis=1)
        else:
            temp2.columns = ['CRS', 'CRS Note']
            temp2['CRS Note'] = temp2['CRS Note'].str.strip('[]')

        temp2['CRS'] = temp2['CRS'].str.replace(r'[()]', '', regex=True).map(
            lambda z: ' and '.join(['{} [{}]'.format(*z_.split('✖')) for z_ in z.split(' &&& ')])
            if ' &&& ' in z else z)

        dat = pd.concat([dat, temp2], axis=1)

        return dat

    @staticmethod
    def _parse_owner_and_operator(x, sep=' / '):
        """
        x = dat['Owner'][0]
        x = dat['Owner'][1]
        """

        if ' / and / ' in x:
            y, y_ = x.replace(' / and / ', ' &&& '), ''

        elif ' / ' in x:
            x_ = x.split(sep)

            # y - Owners or operators; y_ - Former owners or operators
            if len(x_) > 1:
                y = x_[0]
                y_ = x_[1] if len(x_[1:]) == 1 else sep.join(x_[1:])
            else:
                y, y_ = x_[0], ''

        else:
            y, y_ = x, ''

        if '✖' in y and ' &&& ' in y:
            y = ' and '.join(['{} [{}]'.format(*z.split('✖')) for z in y.split(' &&& ')])

        return y, y_

    def parse_owner_and_operator_columns(self, dat):
        """
        Parse ``'Owner'`` and ``'Operator'`` of the station locations data.

        :param dat: preprocessed data of the station locations
        :type dat: pandas.DataFrame
        :return: data with parsed information of owners and operators
        :rtype: pandas.DataFrame
        """

        owner_operator = []
        for col in ['Owner', 'Operator']:
            temp = pd.DataFrame(
                dat[col].map(self._parse_owner_and_operator).to_list(), columns=[col, 'Former ' + col])
            del dat[col]
            owner_operator.append(temp)

        dat = pd.concat([dat] + owner_operator, axis=1)

        return dat

    @staticmethod
    def parse_elr_mileage_columns(dat):
        """
        Parse ``'ELR'`` and ``'Mileage'`` of the station locations data.

        :param dat: preprocessed data of the station locations
        :type dat: pandas.DataFrame
        :return: data with parsed ``'ELR'`` and ``'Mileage'``
        :rtype: pandas.DataFrame
        """

        dat['Mileage'] = dat['Mileage'].map(lambda x: ']'.join(x.replace(' / (', ' [').rsplit(')', 1)))

        em_col_names = ['ELR', 'Mileage']
        dat[em_col_names] = dat[em_col_names].applymap(
            lambda x: x.replace(' /  / ', ' / ').replace(' /  [', ' [').split(' / ')
            if ' / ' in x else x)

        # Where the Mileage data indicates the start and end
        idx = dat[dat[em_col_names].apply(
            lambda x: len(x.Mileage) != len(x.ELR) and isinstance(x.Mileage, list),
            axis=1)].index
        dat.loc[idx, 'Mileage'] = dat.loc[idx, 'Mileage'].map(lambda x: ' - '.join(x))

        return dat

    def collect_locations_by_initial(self, initial, update=False, verbose=False):
        """
        Collect `data of railway station locations
        <http://www.railwaycodes.org.uk/stations/station0.shtm>`_
        (mileages, operators and grid coordinates) for a given initial letter.

        :param initial: initial letter of locations of the railway station data
        :type initial: str
        :param update: whether to do an update check (for the package data), defaults to ``False``
        :type update: bool
        :param verbose: whether to print relevant information in console, defaults to ``False``
        :type verbose: bool or int
        :return: data of railway station locations beginning with the given initial letter and
            date of when the data was last updated
        :rtype: dict

        **Examples**::

            >>> from pyrcs.other_assets import Stations  # from pyrcs import Stations

            >>> stn = Stations()

            >>> stn_loc_a_codes = stn.collect_locations_by_initial(initial='a')
            >>> type(stn_loc_a_codes)
            dict
            >>> list(stn_loc_a_codes.keys())
            ['A', 'Last updated date']

            >>> stn_loc_a_codes_dat = stn_loc_a_codes['A']
            >>> type(stn_loc_a_codes_dat)
            pandas.core.frame.DataFrame
            >>> stn_loc_a_codes_dat.head()
                  Station  ...                                    Former Operator
            0  Abbey Wood  ...  London & South Eastern Railway from 1 April 20...
            1  Abbey Wood  ...  London & South Eastern Railway from 1 April 20...
            2        Aber  ...  Keolis Amey Operations/Gweithrediadau Keolis A...
            3   Abercynon  ...  Keolis Amey Operations/Gweithrediadau Keolis A...
            4   Abercynon  ...  Keolis Amey Operations/Gweithrediadau Keolis A...
            [5 rows x 14 columns]
            >>> stn_loc_a_codes_dat.columns.to_list()
            ['Station',
             'Station Note',
             'ELR',
             'Mileage',
             'Status',
             'Degrees Longitude',
             'Degrees Latitude',
             'Grid Reference',
             'CRS',
             'CRS Note',
             'Owner',
             'Former Owner',
             'Operator',
             'Former Operator']
            >>> stn_loc_a_codes_dat[['Station', 'ELR', 'Mileage']].head()
                  Station  ELR   Mileage
            0  Abbey Wood  NKL  11m 43ch
            1  Abbey Wood  XRS  24.458km
            2        Aber  CAR   8m 69ch
            3   Abercynon  CAM  16m 28ch
            4   Abercynon  ABD  16m 28ch
        """

        beginning_with = validate_initial(initial)
        initial_ = beginning_with.lower()

        ext = ".pickle"
        path_to_pickle = self._cdd("a-z", initial_ + ext)

        if os.path.isfile(path_to_pickle) and not update:
            data = load_data(path_to_pickle)

        else:
            if verbose == 2:
                print("Collecting data of {} of stations beginning with '{}')".format(
                    self.KEY_TO_STN.lower(), beginning_with), end=" ... ")

            data = {beginning_with: None, self.KEY_TO_LAST_UPDATED_DATE: None}

            # url = stn.URL.replace('station0', 'station{}'.format(beginning_with.lower()))
            url = self.URL.replace('station0', 'station{}'.format(initial_))
            try:
                source = requests.get(url=url, headers=fake_requests_headers())
            except Exception as e:
                if verbose == 2:
                    print("Failed. ", end="")
                print_inst_conn_err(verbose=verbose, e=e)

            else:
                try:
                    soup = bs4.BeautifulSoup(markup=source.content, features='html.parser')
                    thead, tbody = soup.find('thead'), soup.find('tbody')

                    if any(x is None for x in {thead, tbody}):
                        if verbose == 2:
                            print(f"There are no stations starting with '{beginning_with}'.")
                            # f"There are no British towns starting with '{beginning_with}'.

                    else:
                        # Create a DataFrame of the requested table
                        trs = tbody.find_all(name='tr')
                        ths = [re.sub(r'\n?\r+\n?', ' ', h.text).strip() for h in thead.find_all('th')]
                        dat = parse_tr(trs=trs, ths=ths, as_dataframe=True)

                        dat_ = dat.copy()

                        parser_funcs = [
                            self.check_row_spans,
                            self.parse_coordinates_columns,
                            self.parse_station_column,
                            self.parse_owner_and_operator_columns,
                            self.parse_elr_mileage_columns,
                        ]
                        for parser_func in parser_funcs:
                            dat_ = parser_func(dat_)

                        # Explode by ELR and Mileage
                        dat_ = dat_.explode(column=['ELR', 'Mileage'], ignore_index=True)

                        data = {
                            beginning_with: dat_.sort_values('Station', ignore_index=True),
                            self.KEY_TO_LAST_UPDATED_DATE: get_last_updated_date(url=url, parsed=True)
                        }

                        if verbose == 2:
                            print("Done.")

                    save_data_to_file(
                        self, data=data, data_name=beginning_with, ext=ext, dump_dir=self._cdd("a-z"),
                        verbose=verbose)

                except Exception as e:
                    print(f"Failed. {format_err_msg(e)}")

        return data

    def fetch_locations(self, update=False, dump_dir=None, verbose=False):
        """
        Fetch `data of railway station locations`_ (mileages, operators and grid coordinates).

        .. _`data of railway station locations`: http://www.railwaycodes.org.uk/stations/station0.shtm

        :param update: whether to do an update check (for the package data), defaults to ``False``
        :type update: bool
        :param dump_dir: name of a folder where the pickle file is to be saved, defaults to ``None``
        :type dump_dir: str or None
        :param verbose: whether to print relevant information in console, defaults to ``False``
        :type verbose: bool or int
        :return: data of railway station locations and date of when the data was last updated
        :rtype: dict

        **Examples**::

            >>> from pyrcs.other_assets import Stations  # from pyrcs import Stations

            >>> stn = Stations()

            >>> stn_loc_codes = stn.fetch_locations()
            >>> type(stn_loc_codes)
            dict
            >>> list(stn_loc_codes.keys())
            ['Mileages, operators and grid coordinates', 'Last updated date']

            >>> stn.KEY_TO_STN
            'Mileages, operators and grid coordinates'

            >>> stn_loc_codes_dat = stn_loc_codes[stn.KEY_TO_STN]
            >>> type(stn_loc_codes_dat)
            pandas.core.frame.DataFrame
            >>> stn_loc_codes_dat.head()
                  Station  ...                                    Former Operator
            0  Abbey Wood  ...  London & South Eastern Railway from 1 April 20...
            1  Abbey Wood  ...  London & South Eastern Railway from 1 April 20...
            2        Aber  ...  Keolis Amey Operations/Gweithrediadau Keolis A...
            3   Abercynon  ...  Keolis Amey Operations/Gweithrediadau Keolis A...
            4   Abercynon  ...  Keolis Amey Operations/Gweithrediadau Keolis A...
            [5 rows x 14 columns]
            >>> stn_loc_codes_dat.columns.to_list()
            ['Station',
             'Station Note',
             'ELR',
             'Mileage',
             'Status',
             'Degrees Longitude',
             'Degrees Latitude',
             'Grid Reference',
             'CRS',
             'CRS Note',
             'Owner',
             'Former Owner',
             'Operator',
             'Former Operator']
            >>> stn_loc_codes_dat[['Station', 'ELR', 'Mileage']].head()
                  Station  ELR   Mileage
            0  Abbey Wood  NKL  11m 43ch
            1  Abbey Wood  XRS  24.458km
            2        Aber  CAR   8m 69ch
            3   Abercynon  CAM  16m 28ch
            4   Abercynon  ABD  16m 28ch
        """

        verbose_1 = collect_in_fetch_verbose(data_dir=dump_dir, verbose=verbose)
        verbose_2 = verbose_1 if is_home_connectable() else False

        data_sets = [
            self.collect_locations_by_initial(initial=x, update=update, verbose=verbose_2)
            for x in string.ascii_lowercase]

        if all(d[x] is None for d, x in zip(data_sets, string.ascii_uppercase)):
            if update:
                print_inst_conn_err(verbose=verbose)
                print_void_msg(data_name=self.KEY_TO_STN, verbose=verbose)

            data_sets = [
                self.collect_locations_by_initial(x, update=False, verbose=verbose_1)
                for x in string.ascii_lowercase
            ]

        stn_dat_tbl_ = (item[x] for item, x in zip(data_sets, string.ascii_uppercase))
        stn_dat_tbl = sorted(
            [x for x in stn_dat_tbl_ if x is not None], key=lambda x: x.shape[1], reverse=True)
        stn_data = pd.concat(stn_dat_tbl, axis=0, ignore_index=True, sort=False)

        stn_data = stn_data.where(pd.notna(stn_data), None)
        stn_data.sort_values(['Station'], inplace=True)

        stn_data.index = range(len(stn_data))

        last_updated_dates = (d[self.KEY_TO_LAST_UPDATED_DATE] for d in data_sets)
        latest_update_date = max(d for d in last_updated_dates if d is not None)

        railway_station_data = {
            self.KEY_TO_STN: stn_data,
            self.KEY_TO_LAST_UPDATED_DATE: latest_update_date,
        }

        if dump_dir is not None:
            save_data_to_file(
                self, data=railway_station_data, data_name=self.KEY_TO_STN, ext=".pickle",
                dump_dir=dump_dir, verbose=verbose)

        return railway_station_data
