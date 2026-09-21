from .google_sheet import get_google_sheet_data


def test_google_sheet():
    data = get_google_sheet_data()

    print("Google Sheet Data:")
    print(data)

    return data