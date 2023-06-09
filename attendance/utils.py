# form validation
import json
import re


def validate_level(level, errors):
    """Validates student level"""
    VALID_LEVELS = '100 200 300 400 500'.split(' ')
    if level not in VALID_LEVELS:
        errors.append(f"{level!r} is not a valid level, select any of {VALID_LEVELS!r}")
    return errors

def validate_phone_number(phone_number, errors):
    """
    Validates phone number
    phone number should
        - start with 0
        - have a 7,8 or 9 as next number i.e 
        - have a 0 or 1 as third number
        - have 8 other digits only
    e.g: 080..., 081..., 090..., 091..., 070..., 071...
    """
    pattern = r"^0[789][01]\d{8}$"
    if re.match(pattern, phone_number) is None:
        errors.append(f"{phone_number!r} does not seem to be valid. (should be in the format 080XXXXXXXX)")
    return errors
    

def validate_reg_num(reg_num, errors):
    """
    Validates reg num

    reg_num should
    - either be 201X or 202X (all 200X should have graduated)
    - have 0-9 as third number
    - have 6 digits after a /
    """
    pattern = r"^20[1-2][0-9]/\d{6}$"
    if re.match(pattern, reg_num) is None:
        errors.append(f"{reg_num!r} is not valid, (should be 201X/XXXX or 202X/XXXXXX)")
    return errors

def get_form_errors(form):
    errors = []
    reg_num = form.get('reg_num')
    phone_number = form.get('phone_number')
    level = form.get('level')

    errors = validate_reg_num(reg_num, errors)
    errors = validate_level(level, errors)
    if phone_number:
        errors = validate_phone_number(phone_number, errors)

    return errors


def student_to_dict(student, mask=None, **kwargs):
    # converts student model to dict
    # discard any keyword that starts with '_'
    # discard any keyword in mask
    # include keyword arguments in dictionary

    res = {}
    for k,v in student.__dict__.items():
        if k.startswith('_'):
            continue
        if mask and k in mask:
            continue
        if k == "arrival_time":
            # get only hour and minute of arrival time
            res[k] = v.arrival_time.strftime("%H : %m")
            continue
        res[k] = v
    res.update(kwargs)
    return res


def json_serialize(_dict):
    """
    Serialize this object to a string, according to the `server-sent events
    specification <https://www.w3.org/TR/eventsource/>`_.
    """
    if isinstance(_dict['data'], str):
        data = _dict['data']
    else:
        data = json.dumps(_dict['data'])
    lines = ["data:{value}".format(value=line) for line in data.splitlines()]

    if _dict['event']:
        lines.insert(0, "event:{value}".format(value=_dict['event']))

    if _dict["retry"]:
        lines.append("retry:{value}".format(value=_dict['retry']))
    return "\n".join(lines) + "\n\n"
