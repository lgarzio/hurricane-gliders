#! /usr/bin/env python3

"""
Author: Lori Garzio on 2/19/2021
Last modified: 2/19/2021
"""


def define_region_limits(region):
    """
    :param region: region of interest
    :return: [lon min, lon max, lat min, lat max]
    """

    if region == 'GoMex':
        limits = [-100, -80, 18, 32]
    return limits
