"""
Windows timezone name → IANA (Olson) timezone name mapping.

Source: Unicode CLDR windowsZones.xml, territory="001" entries.
https://github.com/unicode-org/cldr/blob/main/common/supplemental/windowsZones.xml

Each key is the Windows/Outlook TZID string as it appears in a VTIMEZONE component.
Each value is the canonical IANA timezone identifier for that zone.

If a TZID is not found in this table it is assumed to already be an IANA name and
is left unchanged.
"""

WINDOWS_TO_IANA: dict[str, str] = {
    # UTC-12
    "Dateline Standard Time":              "Etc/GMT+12",
    # UTC-11
    "UTC-11":                              "Etc/GMT+11",
    # UTC-10
    "Aleutian Standard Time":             "America/Adak",
    "Hawaiian Standard Time":             "Pacific/Honolulu",
    # UTC-09:30
    "Marquesas Standard Time":            "Pacific/Marquesas",
    # UTC-09
    "Alaskan Standard Time":              "America/Anchorage",
    "UTC-09":                             "Etc/GMT+9",
    # UTC-08
    "Pacific Standard Time (Mexico)":     "America/Tijuana",
    "UTC-08":                             "Etc/GMT+8",
    "Pacific Standard Time":              "America/Los_Angeles",
    # UTC-07
    "US Mountain Standard Time":          "America/Phoenix",
    "Mountain Standard Time (Mexico)":    "America/Mazatlan",
    "Mountain Standard Time":             "America/Denver",
    "Yukon Standard Time":                "America/Whitehorse",
    # UTC-06
    "Central America Standard Time":      "America/Guatemala",
    "Central Standard Time":              "America/Chicago",
    "Easter Island Standard Time":        "Pacific/Easter",
    "Central Standard Time (Mexico)":     "America/Mexico_City",
    "Canada Central Standard Time":       "America/Regina",
    # UTC-05
    "SA Pacific Standard Time":           "America/Bogota",
    "Eastern Standard Time (Mexico)":     "America/Cancun",
    "Eastern Standard Time":              "America/New_York",
    "Haiti Standard Time":                "America/Port-au-Prince",
    "Cuba Standard Time":                 "America/Havana",
    "US Eastern Standard Time":           "America/Indiana/Indianapolis",
    "Turks And Caicos Standard Time":     "America/Grand_Turk",
    # UTC-04
    "Paraguay Standard Time":             "America/Asuncion",
    "Atlantic Standard Time":             "America/Halifax",
    "Venezuela Standard Time":            "America/Caracas",
    "Central Brazilian Standard Time":    "America/Cuiaba",
    "SA Western Standard Time":           "America/La_Paz",
    "Pacific SA Standard Time":           "America/Santiago",
    # UTC-03:30
    "Newfoundland Standard Time":         "America/St_Johns",
    # UTC-03
    "Tocantins Standard Time":            "America/Araguaina",
    "E. South America Standard Time":     "America/Sao_Paulo",
    "SA Eastern Standard Time":           "America/Cayenne",
    "Argentina Standard Time":            "America/Argentina/Buenos_Aires",
    "Greenland Standard Time":            "America/Godthab",
    "Montevideo Standard Time":           "America/Montevideo",
    "Magallanes Standard Time":           "America/Punta_Arenas",
    "Saint Pierre Standard Time":         "America/Miquelon",
    "Bahia Standard Time":                "America/Bahia",
    # UTC-02
    "UTC-02":                             "Etc/GMT+2",
    "Mid-Atlantic Standard Time":         "Etc/GMT+2",
    # UTC-01
    "Azores Standard Time":               "Atlantic/Azores",
    "Cape Verde Standard Time":           "Atlantic/Cape_Verde",
    # UTC+00
    "UTC":                                "Etc/GMT",
    "GMT Standard Time":                  "Europe/London",
    "Greenwich Standard Time":            "Atlantic/Reykjavik",
    "Sao Tome Standard Time":             "Africa/Sao_Tome",
    "Morocco Standard Time":              "Africa/Casablanca",
    # UTC+01
    "W. Europe Standard Time":            "Europe/Berlin",
    "Central Europe Standard Time":       "Europe/Budapest",
    "Romance Standard Time":              "Europe/Paris",
    "Central European Standard Time":     "Europe/Warsaw",
    "W. Central Africa Standard Time":    "Africa/Lagos",
    # UTC+02
    "Jordan Standard Time":               "Asia/Amman",
    "GTB Standard Time":                  "Europe/Bucharest",
    "Middle East Standard Time":          "Asia/Beirut",
    "Egypt Standard Time":                "Africa/Cairo",
    "E. Europe Standard Time":            "Asia/Nicosia",
    "Syria Standard Time":                "Asia/Damascus",
    "West Bank Standard Time":            "Asia/Hebron",
    "South Africa Standard Time":         "Africa/Johannesburg",
    "FLE Standard Time":                  "Europe/Kiev",
    "Israel Standard Time":               "Asia/Jerusalem",
    "Kaliningrad Standard Time":          "Europe/Kaliningrad",
    "Sudan Standard Time":                "Africa/Khartoum",
    "Libya Standard Time":                "Africa/Tripoli",
    "Namibia Standard Time":              "Africa/Windhoek",
    # UTC+03
    "Arabic Standard Time":               "Asia/Baghdad",
    "Turkey Standard Time":               "Europe/Istanbul",
    "Arab Standard Time":                 "Asia/Riyadh",
    "Belarus Standard Time":              "Europe/Minsk",
    "Russian Standard Time":              "Europe/Moscow",
    "E. Africa Standard Time":            "Africa/Nairobi",
    # UTC+03:30
    "Iran Standard Time":                 "Asia/Tehran",
    # UTC+04
    "Arabian Standard Time":              "Asia/Dubai",
    "Astrakhan Standard Time":            "Europe/Astrakhan",
    "Azerbaijan Standard Time":           "Asia/Baku",
    "Russia Time Zone 3":                 "Europe/Samara",
    "Mauritius Standard Time":            "Indian/Mauritius",
    "Saratov Standard Time":              "Europe/Saratov",
    "Georgian Standard Time":             "Asia/Tbilisi",
    "Volga Standard Time":                "Europe/Ulyanovsk",
    "Caucasus Standard Time":             "Asia/Yerevan",
    # UTC+04:30
    "Afghanistan Standard Time":          "Asia/Kabul",
    # UTC+05
    "West Asia Standard Time":            "Asia/Tashkent",
    "Ekaterinburg Standard Time":         "Asia/Yekaterinburg",
    "Pakistan Standard Time":             "Asia/Karachi",
    "Qyzylorda Standard Time":            "Asia/Qyzylorda",
    # UTC+05:30
    "India Standard Time":                "Asia/Calcutta",
    "Sri Lanka Standard Time":            "Asia/Colombo",
    # UTC+05:45
    "Nepal Standard Time":                "Asia/Katmandu",
    # UTC+06
    "Central Asia Standard Time":         "Asia/Almaty",
    "Bangladesh Standard Time":           "Asia/Dhaka",
    "Omsk Standard Time":                 "Asia/Omsk",
    # UTC+06:30
    "Myanmar Standard Time":              "Asia/Rangoon",
    # UTC+07
    "SE Asia Standard Time":              "Asia/Bangkok",
    "Altai Standard Time":                "Asia/Barnaul",
    "W. Mongolia Standard Time":          "Asia/Hovd",
    "North Asia Standard Time":           "Asia/Krasnoyarsk",
    "N. Central Asia Standard Time":      "Asia/Novosibirsk",
    "Tomsk Standard Time":                "Asia/Tomsk",
    # UTC+08
    "China Standard Time":                "Asia/Shanghai",
    "North Asia East Standard Time":      "Asia/Irkutsk",
    "Singapore Standard Time":            "Asia/Singapore",
    "W. Australia Standard Time":         "Australia/Perth",
    "Taipei Standard Time":               "Asia/Taipei",
    "Ulaanbaatar Standard Time":          "Asia/Ulaanbaatar",
    # UTC+08:45
    "Aus Central W. Standard Time":       "Australia/Eucla",
    # UTC+09
    "Transbaikal Standard Time":          "Asia/Chita",
    "Tokyo Standard Time":                "Asia/Tokyo",
    "North Korea Standard Time":          "Asia/Pyongyang",
    "Korea Standard Time":                "Asia/Seoul",
    "Yakutsk Standard Time":              "Asia/Yakutsk",
    # UTC+09:30
    "Cen. Australia Standard Time":       "Australia/Adelaide",
    "AUS Central Standard Time":          "Australia/Darwin",
    # UTC+10
    "E. Australia Standard Time":         "Australia/Brisbane",
    "AUS Eastern Standard Time":          "Australia/Sydney",
    "West Pacific Standard Time":         "Pacific/Port_Moresby",
    "Tasmania Standard Time":             "Australia/Hobart",
    "Vladivostok Standard Time":          "Asia/Vladivostok",
    # UTC+10:30
    "Lord Howe Standard Time":            "Australia/Lord_Howe",
    # UTC+11
    "Bougainville Standard Time":         "Pacific/Bougainville",
    "Russia Time Zone 10":                "Asia/Srednekolymsk",
    "Magadan Standard Time":              "Asia/Magadan",
    "Norfolk Standard Time":              "Pacific/Norfolk",
    "Sakhalin Standard Time":             "Asia/Sakhalin",
    "Central Pacific Standard Time":      "Pacific/Guadalcanal",
    # UTC+12
    "Russia Time Zone 11":                "Asia/Kamchatka",
    "New Zealand Standard Time":          "Pacific/Auckland",
    "UTC+12":                             "Etc/GMT-12",
    "Fiji Standard Time":                 "Pacific/Fiji",
    # UTC+12:45
    "Chatham Islands Standard Time":      "Pacific/Chatham",
    # UTC+13
    "UTC+13":                             "Etc/GMT-13",
    "Tonga Standard Time":                "Pacific/Tongatapu",
    "Samoa Standard Time":                "Pacific/Apia",
    # UTC+14
    "Line Islands Standard Time":         "Pacific/Kiritimati",
}
