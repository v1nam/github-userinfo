import requests
import argparse
import sys
import itertools
import time
import os
from concurrent import futures
from collections import Counter

success = "\033[92m"
fail = "\033[91m"
warn = "\033[93m"

cyan = "\u001b[36m"
blue = "\033[0;34m"
gray = "\033[0;37m"
light_green = "\033[1;32m"
yellow = "\033[1;33m"

end = "\033[0m"

languages = {
    "Python": " ",
    "Rust": " ",
    "Assembly": "",
    "Shell": " ",
    "Vim script": " ",
    "HTML": " ",
    "JavaScript": " ",
    "CSS": " ",
    "Elixir": " ",
    "C#": " ",
    "C++": " ",
    "C": " ",
    "PHP": " ",
    "Go": " ",
    "Perl": " ",
    "TeX": "",
    "Swift": " ",
    "TypeScript": " ",
    "Ruby": " ",
    "Julia": " ",
    "Scala": " ",
    "Java": " ",
    "Erlang": " ",
    "CoffeeScript": " ",
}


def get_lang(ls):
    try:
        langs = [i["language"] for i in ls if i["language"]]
        lang = Counter(langs).most_common(1)[0][0]
    except IndexError:
        return "No languages used"
    try:
        return languages[lang] + lang
    except KeyError:
        return lang


uname_parse = argparse.ArgumentParser(
    prog="ghinfo",
    description="Get the github info on the username mentioned",
    usage="%(prog)s [options] username",
)

uname_parse.add_argument(
    "username",
    type=str,
    help="The github username of the person\
    you want the info on",
)

username = uname_parse.parse_args().username

is_done = False

loading_ls = [
    "[=    ]",
    "[ =   ]",
    "[  =  ]",
    "[   = ]",
    "[    =]",
]

loading_ls += loading_ls[::-1]


def thread_func():
    global is_done
    url = f"https://api.github.com/users/{username}"
    info_response = requests.get(url)
    repo_resp = ""
    if info_response.json().get("message") is None:
        repo_resp = requests.get(info_response.json()["repos_url"])
    is_done = True
    return info_response, repo_resp


def main():
    global is_done
    with futures.ThreadPoolExecutor() as executor:
        future = executor.submit(thread_func)

        for c in itertools.cycle(loading_ls):
            if not is_done:
                sys.stdout.write(f"{warn}\rFetching info " + c + end)
                sys.stdout.flush()
                time.sleep(0.12)
            else:
                sys.stdout.write(f'\r{" "*21}')
                sys.stdout.flush()
                break

    val = future.result()

    info_dict = val[0].json()

    if info_dict.get("message") is not None:
        print(f"\n{fail} Invalid user, User not found{end}")

    else:
        repos = val[1].json()
        print(f"\n{success} Success!{end}\n")

        created_at = info_dict.get("created_at")

        final_info = {
            f"{light_green}{end} Name": f"{info_dict.get('name')}",
            " Company": f"{info_dict.get('company')}",
            f"{fail}{end} Location": f"{info_dict.get('location')}",
            f"{warn}{end} Public Repos": f"{info_dict.get('public_repos')}",
            f"{gray}{end} Public gists": f"{info_dict.get('public_gists')}",
            f"{cyan}{end} Followers": f"{info_dict.get('followers')}",
            f"{blue}{end} Following": f"{info_dict.get('following')}",
            " Creation Date": f"{created_at[:created_at.find('T')]}",
            f"{cyan} {end}Most used language": get_lang(repos),
            f"{yellow}{end} Description": f"\n{info_dict.get('bio')}",
        }

        print("\n".join([f"{key}: {val}" for key, val in final_info.items()]))


try:
    main()
except KeyboardInterrupt:
    print("\nInterrupted by user ⏎")
    try:
        sys.exit(0)
    except SystemExit:
        os._exit(0)
