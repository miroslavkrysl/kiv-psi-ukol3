from datetime import datetime, timedelta

import requests

ISS_NOW_LOCATION = "http://api.open-notify.org/iss-now.json"
SUNRISE_SUNSET_LOCATION = "https://api.sunrise-sunset.org/json"

DATETIME_FORMAT = "%d. %m. %Y %H:%M"

SUN_HOURS_MIN = 1
SUN_HOURS_MAX = 2


def main():
    """
    Main function of the program.
    It sends requests to Open Notify server to get information about ISS
    from ISS Location Now service and times of sunset, sunrise and solar noon
    from Sunrise Sunset service.
    Received data is used to determine observation conditions on the current ISS location.
    """

    # --- Get data about ISS ---
    try:
        response = requests.get(ISS_NOW_LOCATION)

        if response.status_code != 200:
            print("Error while fetching data from ISS Location Now service: " + response.reason)

        json = response.json()
        latitude = json['iss_position']['latitude']
        longitude = json['iss_position']['longitude']

        try:
            time = datetime.utcfromtimestamp(json['timestamp'])

        except ValueError:
            print("Error while fetching data from ISS Location Now service. Timestamp is in invalid format.")
            return

    except ConnectionError:
        print("Can not connect to ISS Location Now service.")
        return
    except ValueError:
        print("Error while fetching data with ISS Location Now service. Response is not a valid JSON.")
        return
    except KeyError:
        print("Error while fetching data with ISS Location Now service. Incorrect JSON keys.")
        return

    # --- Get sunrise, sunset and solar noon times ---
    try:
        response = requests.get(SUNRISE_SUNSET_LOCATION, params={
            "lat": latitude,
            "lng": longitude,
            "formatted": 0
        })

        if response.status_code != 200:
            print("Error while fetching data from Sunrise Sunset service: " + response.reason)

        json = response.json()

        try:
            # the `-6` is for removing timezone offset (+00:00)
            sunrise = datetime.fromisoformat(json['results']['sunrise'][:-6])
            sunset = datetime.fromisoformat(json['results']['sunset'][:-6])
            solar_noon = datetime.fromisoformat(json['results']['solar_noon'][:-6])

        except ValueError:
            print("Error while fetching data from Sunrise Sunset service. Times is not in valid format.")
            return

    except ConnectionError:
        print("Can not connect to from Sunrise Sunset service.")
        return
    except ValueError:
        print("Error while fetching data from Sunrise Sunset service. Response is not a valid JSON.")
        return
    except KeyError:
        print("Error while fetching data from Sunrise Sunset service. Incorrect JSON keys.")
        return

    # compute day/night
    day = True
    if time < sunrise or time > sunset:
        day = False

    # compute before/after sunrise/sunset
    if time <= sunrise:
        phase_delta = sunrise - time
        phase_text = "before sunrise"
    elif time <= solar_noon:
        phase_delta = time - sunrise
        phase_text = "after sunrise"
    elif time <= sunset:
        phase_delta = sunset - time
        phase_text = "before sunset"
    else:
        phase_delta = time - sunset
        phase_text = "after sunset"

    phase_delta_text = "%.2d:%.2d" % (
        phase_delta.seconds // 3600 % 24,
        phase_delta.seconds // 60 % 60
    )

    # compute observing conditions
    ideal = False
    if sunrise - timedelta(hours=SUN_HOURS_MAX) <= time <= sunrise - timedelta(hours=SUN_HOURS_MIN) \
            or sunset + timedelta(hours=SUN_HOURS_MIN) <= time <= sunset + timedelta(hours=SUN_HOURS_MAX):
        ideal = True

    print("-------------------- ISS location ---------------------")
    print(f"latitude:\t\t\t\t\t{latitude:>8}")
    print(f"longitude:\t\t\t\t\t{longitude:>8}")
    print(f"UTC time:\t\t\t\t\t", time.strftime(DATETIME_FORMAT))
    print("day/night:\t\t\t\t\t", "day" if day else "night")
    print("day phase:\t\t\t\t\t", phase_delta_text, phase_text)
    print("observation conditions:\t\t", "ideal" if ideal else "not ideal")


if __name__ == '__main__':
    main()