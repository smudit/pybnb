import json
import os
from datetime import datetime
from urllib.parse import urlencode

from curl_cffi import requests
from dotenv import load_dotenv

import gobnb.api as api
from gobnb.standardize import get_nested_value, standardize_search

load_dotenv()

CACHE_DIR = os.getenv("CACHE_DIR")

treament = [
    "feed_map_decouple_m11_treatment",
    "m1_2024_monthly_stays_dial_treatment_flag",
    "recommended_amenities_2024_treatment_a",
    "filter_redesign_2024_treatment",
    "filter_reordering_2024_roomtype_treatment",
]


def Search_all(
    check_in: str,
    check_out: str,
    ne_lat: float,
    ne_long: float,
    sw_lat: float,
    sw_long: float,
    zoom_value: int,
    currency: str,
    proxy_url: str,
):
    api_key = api.get(proxy_url)
    all_results = []
    cursor = ""
    while True:
        results_raw = search(
            check_in,
            check_out,
            ne_lat,
            ne_long,
            sw_lat,
            sw_long,
            zoom_value,
            cursor,
            currency,
            api_key,
            proxy_url,
        )
        results = standardize_search(results_raw.get("searchResults", []))
        all_results = all_results + results
        if (
            len(results) == 0
            or "nextPageCursor" not in results_raw["paginationInfo"]
            or results_raw["paginationInfo"]["nextPageCursor"] is None
        ):
            break
        cursor = results_raw["paginationInfo"]["nextPageCursor"]
    return all_results


def Search_first_page(
    check_in: str,
    check_out: str,
    ne_lat: float,
    ne_long: float,
    sw_lat: float,
    sw_long: float,
    zoom_value: int,
    cursor: str,
    currency: str,
    proxy_url: str,
):
    api_key = api.get(proxy_url)
    results = search(
        check_in,
        check_out,
        ne_lat,
        ne_long,
        sw_lat,
        sw_long,
        zoom_value,
        "",
        currency,
        api_key,
        proxy_url,
    )
    results = standardize_search(results)
    return results


def search(
    check_in: str,
    check_out: str,
    ne_lat: float,
    ne_long: float,
    sw_lat: float,
    sw_long: float,
    zoom_value: int,
    cursor: str,
    currency: str,
    api_key: str,
    proxy_url: str,
):
    check_in_date = datetime.strptime(check_in, "%Y-%m-%d")
    check_out_date = datetime.strptime(check_out, "%Y-%m-%d")

    difference = check_out_date - check_in_date

    days = difference.days

    base_url = "https://www.airbnb.com/api/v3/StaysSearch/d4d9503616dc72ab220ed8dcf17f166816dccb2593e7b4625c91c3fce3a3b3d6"
    query_params = {
        "operationName": "StaysSearch",
        "locale": "en",
        "currency": currency,
    }
    url_parsed = f"{base_url}?{urlencode(query_params)}"
    rawParams = [
        {"filterName": "cdnCacheSafe", "filterValues": ["false"]},
        {"filterName": "channel", "filterValues": ["EXPLORE"]},
        {"filterName": "checkin", "filterValues": [check_in]},
        {"filterName": "checkout", "filterValues": [check_out]},
        {"filterName": "datePickerType", "filterValues": ["calendar"]},
        {"filterName": "flexibleTripLengths", "filterValues": ["one_week"]},
        {
            "filterName": "itemsPerGrid",
            "filterValues": ["50"],
        },  # if you read this, this is items returned number, this can bex exploited  ;)
        {"filterName": "monthlyLength", "filterValues": ["3"]},
        {"filterName": "monthlyStartDate", "filterValues": ["2024-02-01"]},
        {"filterName": "neLat", "filterValues": [str(ne_lat)]},
        {"filterName": "neLng", "filterValues": [str(ne_long)]},
        {"filterName": "placeId", "filterValues": ["ChIJpTeBx6wjq5oROJeXkPCSSSo"]},
        {"filterName": "priceFilterInputType", "filterValues": ["0"]},
        {"filterName": "priceFilterNumNights", "filterValues": [str(days)]},
        {"filterName": "query", "filterValues": ["Galapagos Island, Ecuador"]},
        {"filterName": "screenSize", "filterValues": ["large"]},
        {"filterName": "refinementPaths", "filterValues": ["/homes"]},
        {"filterName": "searchByMap", "filterValues": ["true"]},
        {"filterName": "swLat", "filterValues": [str(sw_lat)]},
        {"filterName": "swLng", "filterValues": [str(sw_long)]},
        {"filterName": "tabId", "filterValues": ["home_tab"]},
        {"filterName": "version", "filterValues": ["1.8.3"]},
        {"filterName": "zoomLevel", "filterValues": [str(zoom_value)]},
    ]
    inputData = {
        "operationName": "StaysSearch",
        "extensions": {
            "persistedQuery": {
                "version": 1,
                "sha256Hash": "d4d9503616dc72ab220ed8dcf17f166816dccb2593e7b4625c91c3fce3a3b3d6",
            },
        },
        "variables": {
            "includeMapResults": True,
            "isLeanTreatment": False,
            "staysMapSearchRequestV2": {
                "cursor": cursor,
                "requestedPageType": "STAYS_SEARCH",
                "metadataOnly": False,
                "source": "structured_search_input_header",
                "searchType": "user_map_move",
                "treatmentFlags": treament,
                "rawParams": rawParams,
            },
            "staysSearchRequest": {
                "cursor": cursor,
                "maxMapItems": 9999,
                "requestedPageType": "STAYS_SEARCH",
                "metadataOnly": False,
                "source": "structured_search_input_header",
                "searchType": "user_map_move",
                "treatmentFlags": treament,
                "rawParams": rawParams,
            },
        },
    }
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "en",
        "Cache-Control": "no-cache",
        "Connection": "close",
        "Pragma": "no-cache",
        "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        "Sec-Ch-Ua-Mobile": "?0",
        "X-Airbnb-Api-Key": api_key,
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    }
    proxies = {}
    if proxy_url:
        proxies = {"http": proxy_url, "https": proxy_url}
    response = requests.post(
        url_parsed,
        json=inputData,
        headers=headers,
        proxies=proxies,
        impersonate="chrome110",
    )
    data = response.json()
    to_return = get_nested_value(data, "data.presentation.staysSearch.results", {})
    return to_return


def search_flexible_dates(
    search_url_params: dict,
    currency: str,
    proxy_url: str,
    standardize_results: bool = False,
    use_cache: bool = True,
):
    api_key = api.get(proxy_url)
    all_results = []
    cursor = ""
    while True:
        results_raw = _search_flexible_cached(
            search_url_params,
            currency,
            proxy_url,
            api_key,
            cursor,
            use_cache,
        )
        results = (
            standardize_search(results_raw.get("searchResults", []))
            if standardize_results
            else results_raw.get("searchResults", [])
        )
        all_results = all_results + results
        if (
            len(results) == 0
            or "nextPageCursor" not in results_raw["paginationInfo"]
            or results_raw["paginationInfo"]["nextPageCursor"] is None
        ):
            break
        cursor = results_raw["paginationInfo"]["nextPageCursor"]
    return all_results


def _search_flexible_cached(
    search_url_params: dict,
    currency: str,
    proxy_url: str,
    api_key: str,
    cursor: str,
    use_cache: bool = True,
):
    cache_key = "_".join(
        [
            search_url_params.get("monthly_start_date", ""),
            search_url_params.get("monthly_end_date", ""),
            currency,
            search_url_params.get("query", "").replace(" ", ""),
            cursor,
        ]
    )
    cache_fp = f"{CACHE_DIR}/{cache_key}.json"

    if use_cache and os.path.exists(cache_fp):
        print(f"Cache hit for {cache_key}")
        with open(cache_fp, "r") as f:
            return json.load(f)
    else:
        print(f"Requesting page for {cache_key}")
        results_raw = _search_flexible(
            search_url_params, currency, proxy_url, api_key, cursor
        )
        with open(cache_fp, "w") as f:
            json.dump(results_raw, f)
        return results_raw


def _search_flexible(
    search_url_params: dict,
    currency: str,
    proxy_url: str,
    api_key: str,
    cursor: str,
):
    base_url = "https://www.airbnb.com/api/v3/StaysSearch/385c60ba2599dad1c62355032d8bbc09d826ae11660be78b16e09eba49c5c605"
    query_params = {
        "operationName": "StaysSearch",
        "locale": "en",
        "currency": currency,
    }
    url_parsed = f"{base_url}?{urlencode(query_params)}"
    rawParams = [
        {"filterName": "cdnCacheSafe", "filterValues": ["false"]},
        {
            "filterName": "channel",
            "filterValues": [search_url_params.get("channel", "EXPLORE")],
        },
        {
            "filterName": "datePickerType",
            "filterValues": [
                search_url_params.get("date_picker_type", "flexible_dates")
            ],
        },
        {
            "filterName": "flexibleTripDates",
            "filterValues": search_url_params.get("flexible_trip_dates", []),
        },
        {
            "filterName": "flexibleTripLengths",
            "filterValues": search_url_params.get("flexible_trip_lengths", []),
        },
        {"filterName": "itemsPerGrid", "filterValues": ["18"]},
        {
            "filterName": "monthlyEndDate",
            "filterValues": [search_url_params.get("monthly_end_date", "")],
        },
        {
            "filterName": "monthlyLength",
            "filterValues": [search_url_params.get("monthly_length", "3")],
        },
        {
            "filterName": "monthlyStartDate",
            "filterValues": [search_url_params.get("monthly_start_date", "")],
        },
        {
            "filterName": "placeId",
            "filterValues": [search_url_params.get("place_id", "")],
        },
        {
            "filterName": "priceFilterInputType",
            "filterValues": [search_url_params.get("price_filter_input_type", "2")],
        },
        {"filterName": "query", "filterValues": [search_url_params.get("query", "")]},
        {
            "filterName": "refinementPaths",
            "filterValues": search_url_params.get("refinement_paths", ["/homes"]),
        },
        {"filterName": "screenSize", "filterValues": ["large"]},
        {
            "filterName": "tabId",
            "filterValues": [search_url_params.get("tab_id", "home_tab")],
        },
        {"filterName": "version", "filterValues": ["1.8.3"]},
    ]
    if "adults" in search_url_params:
        rawParams.append(
            {"filterName": "adults", "filterValues": [search_url_params["adults"]]}
        )
    if "location_bb" in search_url_params:
        rawParams.append(
            {
                "filterName": "locationBB",
                "filterValues": [search_url_params["location_bb"]],
            }
        )
    if "source" in search_url_params:
        rawParams.append(
            {"filterName": "source", "filterValues": [search_url_params["source"]]}
        )
    if "search_type" in search_url_params:
        rawParams.append(
            {
                "filterName": "searchType",
                "filterValues": [search_url_params["search_type"]],
            }
        )

    inputData = {
        "operationName": "StaysSearch",
        "variables": {
            "staysSearchRequest": {
                "cursor": cursor,
                "requestedPageType": "STAYS_SEARCH",
                "metadataOnly": "false",
                "source": "structured_search_input_header",
                "searchType": "autocomplete_click",
                "treatmentFlags": [
                    "feed_map_decouple_m11_treatment",
                    "stays_search_rehydration_treatment_desktop",
                    "stays_search_rehydration_treatment_moweb",
                    "m1_2024_monthly_stays_dial_treatment_flag",
                    "recommended_amenities_2024_treatment_b",
                    "filter_redesign_2024_treatment",
                    "filter_reordering_2024_roomtype_treatment",
                ],
                "rawParams": rawParams,
                "maxMapItems": 9999,
            },
            "isLeanTreatment": "false",
        },
        "extensions": {
            "persistedQuery": {
                "version": 1,
                "sha256Hash": "385c60ba2599dad1c62355032d8bbc09d826ae11660be78b16e09eba49c5c605",
            }
        },
    }

    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "en",
        "Cache-Control": "no-cache",
        "Connection": "close",
        "Pragma": "no-cache",
        "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        "Sec-Ch-Ua-Mobile": "?0",
        "X-Airbnb-Api-Key": api_key,
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    }
    proxies = {}
    if proxy_url:
        proxies = {"http": proxy_url, "https": proxy_url}
    response = requests.post(
        url_parsed,
        json=inputData,
        headers=headers,
        proxies=proxies,
        impersonate="chrome110",
    )
    data = response.json()
    to_return = get_nested_value(data, "data.presentation.staysSearch.results", {})
    return to_return
