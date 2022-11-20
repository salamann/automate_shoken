import argparse

from cruise import read_config, wrapper, send_email


def run(args):
    configs = read_config()
    instance_names: list = args.names
    text = ""
    for instance_name in instance_names:
        config = configs[instance_name]
        response = wrapper(config)
        if response == True:
            color = "DarkBlue"
        else:
            color = "DarkGray"
        text += f'<div><span style="font-weight:700;">{instance_name}</span>: <span style="color:{color};">{response}</span></div>'
    return text


def send_email_with_text(text):

    from config import from_email, to_email
    from config import smtp_server, smtp_port_number, smtp_user_name, smtp_password
    send_email(to_email, '今日の自動取引', text, smtp_server, smtp_port_number, smtp_user_name,
               smtp_password, from_email)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='command line interface for automate shoken')
    parser.add_argument('names', nargs='*')
    # args = parser.parse_args(["nikkofloggy"])

    args = parser.parse_args()
    text = run(args)
    send_email_with_text(text)
    pass
