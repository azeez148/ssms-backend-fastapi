def format_phone_number(phone_number: str) -> str:
    """
    Formats a phone number to the +91XXXXXXXXXX format.
    """
    if not phone_number:
        raise ValueError("Phone number cannot be empty")

    phone_number = phone_number.strip()

    if phone_number.startswith('+91'):
        if len(phone_number[3:]) == 10 and phone_number[3:].isdigit():
            return phone_number
        else:
            raise ValueError("Invalid phone number with +91 prefix")
    elif phone_number.startswith('0'):
        if len(phone_number[1:]) == 10 and phone_number[1:].isdigit():
            return f"+91{phone_number[1:]}"
        else:
            raise ValueError("Invalid phone number with 0 prefix")
    elif len(phone_number) == 10 and phone_number.isdigit():
        return f"+91{phone_number}"
    else:
        raise ValueError("Phone number must be 10 digits, or start with 0 or +91")
