# Copyright (c) 2016-2022 Association of Universities for Research in Astronomy, Inc. (AURA)
# For license information see LICENSE or https://opensource.org/licenses/BSD-3-Clause

"""This will have to be customized by a given observatory if used independently
    of Gemini.
"""

from enum import Enum
from typing import Optional, final

import pytz
from astropy.coordinates import EarthLocation, UnknownSiteException

from lucupy.decorators import immutable
from lucupy.minimodel.resource import Resource


@final
@immutable
class Site(Enum):
    """The sites belonging to the observatory using the Scheduler.

    Attributes:
        GN: Gemini North (568@399)
        GS: Gemini South (I11@399)

    """
    GN = ('Gemini North', '568@399')
    GS = ('Gemini South', 'I11@399')

    def __init__(self, site_name: str,
                 coordinate_center: str,
                 *,
                 location: Optional[EarthLocation] = None,
                 timezone: Optional[pytz.BaseTzInfo] = None,
                 resource: Optional[Resource] = None):
        """
        Perform the necessary initialization for a Site object, which is also a Resource.
        Args:
            site_name: the name of the site
            coordinate_center: the coordinate center of the site (probably not needed)
            location: the EarthLocation of the site, which, if not provided, will be looked up by the site_name
            timezone: the pytz timezone at the location which, if not provided, will be looked up by location
            resource: a Resource representing the site, which, if not provided, will be created with id site_name

        Note: if outdated information is found during lookups (e.g. time zone information is not what one would expect),
        this may be because AstroPy downloads and caches this data. Clearing the cache to force a re-download may help:

        import astropy.utils.data
        astropy.utils.data.clear_download_cache()
        """
        self.site_name = site_name
        self.coordinate_center = coordinate_center

        if location is not None:
            self.location = location
        else:
            try:
                self.location = EarthLocation.of_site(site_name)
            except UnknownSiteException as ex:
                msg = f'AstroPy cannot resolve site lookup for location: "{site_name}".'
                raise ValueError(ex, msg)

        if timezone is not None:
            self.timezone = timezone
        else:
            timezone_name = self.location.info.meta['timezone']
            try:
                self.timezone = pytz.timezone(timezone_name)
            except pytz.UnknownTimeZoneError as e:
                msg = f'pytz cannot resolve time zone lookup: {timezone_name}.'
                raise ValueError(e, msg)

        if resource is not None:
            self.resource = resource
        else:
            self.resource = Resource(id=site_name)


# A variable to work with all the sites in scheduler components as a frozenset.
ALL_SITES = frozenset(s for s in Site)
