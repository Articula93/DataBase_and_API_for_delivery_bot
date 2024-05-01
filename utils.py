
def extract_phone(phone):
    list_digit = []
    for ch in phone:
        if ch.isdigit():
            list_digit.append(ch)
    if list_digit[0]=='8' or list_digit[0]=='7':
        list_digit[0]='+7'
    else:
        list_digit.insert(0,'+7')
    return "".join(list_digit)