from concurrent.futures.thread import ThreadPoolExecutor
from datetime import datetime, timedelta

import requests

ISS_NOW_LOCATION = "http://api.open-notify.org/iss-now.json"
SUNRISE_SUNSET_LOCATION = "https://api.sunrise-sunset.org/json"

DATETIME_FORMAT = "%d. %m. %Y %H:%M"

PHASE_DELTA_MIN = 3600  # 1 hour
PHASE_DELTA_MAX = 7200  # 2 hours


def get_iss():
    """
    Get ISS position and time.
    """
    try:
        response = requests.get(ISS_NOW_LOCATION)

        if response.status_code != 200:
            print("Error while fetching data from ISS Location Now service: " + response.reason)

        json = response.json()

        try:
            return {
                "time": datetime.utcfromtimestamp(json['timestamp']),
                "latitude": json['iss_position']['latitude'],
                "longitude": json['iss_position']['longitude']
            }
        except ValueError:
            print("Error while fetching data from ISS Location Now service. Timestamp is in invalid format.")
            return None

    except requests.ConnectionError:
        print("Can not connect to ISS Location Now service.")
        return None
    except ValueError:
        print("Error while fetching data with ISS Location Now service. Response is not a valid JSON.")
        return None
    except KeyError:
        print("Error while fetching data with ISS Location Now service. Incorrect JSON keys.")
        return None


def get_times(date, latitude, longitude):
    """
    Get sunset and sunrise times.
    """
    try:
        response = requests.get(SUNRISE_SUNSET_LOCATION, params={
            "lat": latitude,
            "lng": longitude,
            "date": date,
            "formatted": 0
        })

        if response.status_code != 200:
            print("Error while fetching data from Sunrise Sunset service: " + response.reason)
            return

        json = response.json()

        try:
            # the `-6` is for removing timezone offset (+00:00)
            return {
                "sunrise": datetime.fromisoformat(json['results']['sunrise'][:-6]),
                "sunset": datetime.fromisoformat(json['results']['sunset'][:-6])
            }
        except ValueError:
            print("Error while fetching data from Sunrise Sunset service. Times is not in valid format.")
            return

    except requests.ConnectionError:
        print("Can not connect to from Sunrise Sunset service.")
        return
    except ValueError:
        print("Error while fetching data from Sunrise Sunset service. Response is not a valid JSON.")
        return
    except KeyError:
        print("Error while fetching data from Sunrise Sunset service. Incorrect JSON keys.")
        return


def main():
    """
    Main function of the program.
    It sends requests to Open Notify - ISS Location Now online service to get information about ISS
    and to Sunrise Sunset online service to get times of sunrise and sunset on current ISS location.
    Received data is used to determine observation conditions on the current ISS location.
    """

    print("Fetching data...")

    # get ISS data
    iss = get_iss()

    time = iss["time"]
    latitude = iss["latitude"]
    longitude = iss["longitude"]

    # get sunrise sunset data
    with ThreadPoolExecutor(max_workers=3) as executor:
        yesterday_task = executor.submit(get_times, time.date() - timedelta(days=1), latitude, longitude)
        today_task = executor.submit(get_times, time.date(), latitude, longitude)
        tomorrow_task = executor.submit(get_times, time.date() + timedelta(days=1), latitude, longitude)

    yesterday = yesterday_task.result()
    today = today_task.result()
    tomorrow = tomorrow_task.result()

    sunset_yesterday = yesterday["sunset"]
    sunrise_today = today["sunrise"]
    sunset_today = today["sunset"]
    sunrise_tomorrow = tomorrow["sunrise"]

    # compute before/after sunrise/sunset
    delta_1_half = (sunrise_today - sunset_yesterday) / 2
    delta_2_half = (sunset_today - sunrise_today) / 2
    delta_3_half = (sunrise_tomorrow - sunset_today) / 2

    if time <= sunset_yesterday:
        phase_delta = sunset_yesterday - time
        phase_text = "before sunset"
        day = True
    elif time <= sunset_yesterday + delta_1_half:
        phase_delta = time - sunset_yesterday
        phase_text = "after sunset"
        day = False
    elif time <= sunrise_today:
        phase_delta = sunrise_today - time
        phase_text = "before sunrise"
        day = False
    elif time <= sunrise_today + delta_2_half:
        phase_delta = time - sunrise_today
        phase_text = "after sunrise"
        day = True
    elif time <= sunset_today:
        phase_delta = sunset_today - time
        phase_text = "before sunset"
        day = True
    elif time <= sunset_today + delta_3_half:
        phase_delta = time - sunset_today
        phase_text = "after sunset"
        day = False
    elif time <= sunrise_tomorrow:
        phase_delta = sunrise_tomorrow - time
        phase_text = "before sunrise"
        day = False
    else:
        phase_delta = time - sunrise_tomorrow
        phase_text = "after sunrise"
        day = True

    phase_delta_text = "%.2d:%.2d" % (
        phase_delta.seconds // 3600 % 24,
        phase_delta.seconds // 60 % 60
    )

    # compute observing conditions
    ideal = False
    if (phase_text == "before sunrise" or phase_text == "after sunset") \
            and PHASE_DELTA_MIN <= phase_delta.seconds <= PHASE_DELTA_MAX:
        ideal = True

    print()
    print("--------------- ISS location ----------------")
    print("{:<25} {:>8}".format("latitude:", latitude))
    print("{:<25} {:>8}".format("longitude:", longitude))
    print("{:<25} {}".format("UTC time:", time.strftime(DATETIME_FORMAT)))
    print("{:<25} {}".format("day/night:", "day" if day else "night"))
    print("{:<25} {} {}".format("day phase:", phase_delta_text, phase_text))
    print("{:<25} {}".format("observation conditions:", "ideal" if ideal else "not ideal"))


if __name__ == '__main__':
    main()
