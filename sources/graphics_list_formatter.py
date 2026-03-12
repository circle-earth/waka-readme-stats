from enum import Enum
from typing import Dict, Tuple, List
from datetime import datetime

from pytz import timezone, utc

from manager_environment import EnvironmentManager as EM
from manager_file import FileManager as FM


DAY_TIME_EMOJI = ["🌞", "🌆", "🌃", "🌙"]  # Emojis, representing different times of day.
DAY_TIME_NAMES = ["Morning", "Daytime", "Evening", "Night"]  # Localization identifiers for different times of day.
WEEK_DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]  # Localization identifiers for different days of week.


class Symbol(Enum):
    """
    Symbol version enum.
    Allows to retrieve symbols pairs by calling `Symbol.get_symbols(version)`.
    """

    VERSION_1 = "█", "░"
    VERSION_2 = "⣿", "⣀"
    VERSION_3 = "⬛", "⬜"

    @staticmethod
    def get_symbols(version: int) -> Tuple[str, str]:
        """
        Retrieves symbols pair for specified version.

        :param version: Required symbols version.
        :returns: Two strings for filled and empty symbol value in a tuple.
        """
        return Symbol[f"VERSION_{version}"].value


def make_graph(percent: float):
    """
    Make text progress bar.
    Length of the progress bar is 25 characters.

    :param percent: Completion percent of the progress bar.
    :return: The string progress bar representation.
    """
    done_block, empty_block = Symbol.get_symbols(EM.SYMBOL_VERSION)
    percent_quart = round(percent / 4)
    return f"{done_block * percent_quart}{empty_block * (25 - percent_quart)}"


def get_icon_url(name: str, category: str = "color") -> str:
    """Helper to get correct icon urls based on user's pattern."""
    name_lower = str(name).lower().replace(' ', '')
    if name_lower == "yml":
        name_lower = "yaml"
    elif name_lower == "vs code":
        name_lower = "vscode"
        
    if category == "ides":
        return f"https://icon-iota-neon.vercel.app/icon/ides/{name_lower}"
    elif category == "os":
        return f"https://icon-iota-neon.vercel.app/icon/os/{name_lower}"
    elif category == "color" or category == "repos":
        return f"https://icon-iota-neon.vercel.app/color/{name_lower}?size=20"
    return f"https://icon-iota-neon.vercel.app/color/{name_lower}?size=20"

def format_time_spent(text: str) -> str:
    """Helper to replace spaces with &nbsp; for time spent."""
    return str(text).replace(" ", "&nbsp;")

def make_list(data: List = None, names: List[str] = None, texts: List[str] = None, percents: List[float] = None, top_num: int = 5, sort: bool = True, title: str = "", category: str = "color", col2_name: str = "Time Spent") -> str:
    """
    Make list of HTML tables displaying progress bars with supportive info.
    Matches the user's custom HTML structure.
    """
    if data is not None:
        names = [value for item in data for key, value in item.items() if key == "name"] if names is None else names
        texts = [value for item in data for key, value in item.items() if key == "text"] if texts is None else texts
        percents = [value for item in data for key, value in item.items() if key == "percent"] if percents is None else percents

    data_tuples = list(zip(names, texts, percents))
    top_data = sorted(data_tuples[:top_num], key=lambda record: record[2], reverse=True) if sort else data_tuples[:top_num]
    
    table_html = f'<div align="center"><table><tr><th colspan="3" align="center">{title}</th></tr><tr>'
    
    if category == "day_night":
         table_html += f'<th width="200" align="left">Time of Day</th><th width="200" align="center">Commit Message</th><th width="400" align="center">Progress</th></tr>'
    elif category == "day_of_week":
         table_html += f'<th width="200" align="left">Day</th><th width="200" align="center">Commit Messages </th><th width="400" align="center">Progress</th></tr>'
    elif category == "repos":
         table_html += f'<th width="200" align="left">Language</th><th width="200" align="center">Repository</th><th width="400" align="center">Progress</th></tr>'
    else:
         table_html += f'<th width="200" align="left">{"Language" if category == "color" else ("Editor" if category == "ides" else "OS")}</th><th width="200" align="center">{col2_name}</th><th width="400" align="center">Progress</th></tr>'

    for n, t, p in top_data:
        # Determine bar parameters
        img_url = f"https://geps.dev/progress/{p:.2f}"
        if category == "day_of_week":
            img_url += "?barColor=4472C4"
            
        # Determine name column HTML
        name_html = ""
        if category in ["day_night", "day_of_week", "projects"]:
            name_html = f"&nbsp;{n}"
        else:
            icon_url = get_icon_url(n, category)
            valign = ' valign="middle"' if category != "color" else ''
            width_attr = ' width="30"' if category in ["ides", "os"] else ''
            alt_attr = f' alt="{n}"'
            name_html = f'<img src="{icon_url}"{width_attr}{alt_attr}{valign}/> &nbsp;{n}'
            if category == "color":
                 name_html = f'<img src="{icon_url}"{alt_attr}/>&nbsp;{n}'
                 if n != "Python":
                      name_html = f'<img src="{icon_url}"{alt_attr} valign="middle"/> {n}'
            
        
        row_html = f'<tr>'
        if category in ["day_night", "day_of_week", "projects"]:
            row_html += f'<td style="white-space: nowrap;">{name_html}</td>'
        elif category == "color" and n == "Python":
             row_html += f'<td style="white-space: nowrap;">{name_html}</td>'
        elif category == "ides" and n == "PyCharm":
             row_html += f'<td style="white-space: nowrap;"><img src="{get_icon_url(n, category)}" alt="{n}" width="30" valign="middle"/>&nbsp;{n}</td>'
        else:
             row_html += f'<td>{name_html}</td>'

        row_html += f'<td align="center">{format_time_spent(t)}</td>'
        row_html += f'<td align="center"><img src="{img_url}" alt="{p}%" width="400" height="40"></td></tr>'
        
        table_html += row_html

    table_html += '</table></div>'
    return table_html


async def make_commit_day_time_list(time_zone: str, repositories: Dict, commit_dates: Dict) -> str:
    """
    Calculate commit-related info, how many commits were made, and at what time of day and day of week.

    :param time_zone: User time zone.
    :param repositories: User repositories list.
    :param commit_dates: User commit data list.
    :returns: string representation of statistics.
    """
    stats = str()
    day_times = [0] * 4  # 0 - 6, 6 - 12, 12 - 18, 18 - 24
    week_days = [0] * 7  # Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday

    for repository in repositories:
        if repository["name"] not in commit_dates.keys():
            continue

        for committed_date in [commit_date for branch in commit_dates[repository["name"]].values() for commit_date in branch.values()]:
            local_date = datetime.strptime(committed_date, "%Y-%m-%dT%H:%M:%SZ")
            date = local_date.replace(tzinfo=utc).astimezone(timezone(time_zone))

            day_times[date.hour // 6] += 1
            week_days[date.isoweekday() - 1] += 1

    sum_day = sum(day_times)
    sum_week = sum(week_days)
    day_times = day_times[1:] + day_times[:1]

    if EM.SHOW_COMMIT:
        dt_names = [f"{DAY_TIME_EMOJI[i]} {FM.t(DAY_TIME_NAMES[i])}" for i in range(len(day_times))]
        dt_texts = [f"{day_time} commits" for day_time in day_times]
        dt_percents = [0 if sum_day == 0 else round((day_time / sum_day) * 100, 2) for day_time in day_times]
        title = FM.t("I am an Early") if sum(day_times[0:2]) >= sum(day_times[2:4]) else FM.t("I am a Night")
        title_str = f" {title} "
        
        stats += f"\n{make_list(names=dt_names, texts=dt_texts, percents=dt_percents, top_num=7, sort=False, title=title_str, category='day_night', col2_name='Commit Message')}\n\n"

    if EM.SHOW_DAYS_OF_WEEK:
        wd_names = [FM.t(week_day) for week_day in WEEK_DAY_NAMES]
        wd_texts = [f"{week_day} commits" for week_day in week_days]
        wd_percents = [0 if sum_week == 0 else round((week_day / sum_week) * 100, 2) for week_day in week_days]
        title_raw = FM.t('I am Most Productive on').replace('%s', '')
        title = f"📅 {title_raw.strip()} {wd_names[wd_percents.index(max(wd_percents))]}"
        stats += f"\n{make_list(names=wd_names, texts=wd_texts, percents=wd_percents, top_num=7, sort=False, title=title, category='day_of_week')}\n\n"

    return stats


def make_language_per_repo_list(repositories: Dict) -> str:
    """
    Calculate language-related info, how many repositories in what language user has.

    :param repositories: User repositories.
    :returns: string representation of statistics.
    """
    language_count = dict()
    repos_with_language = [repo for repo in repositories if repo["primaryLanguage"] is not None]
    for repo in repos_with_language:
        language = repo["primaryLanguage"]["name"]
        language_count[language] = language_count.get(language, {"count": 0})
        language_count[language]["count"] += 1

    names = list(language_count.keys())
    texts = [f"{language_count[lang]['count']} {'repo' if language_count[lang]['count'] == 1 else 'repos'}" for lang in names]
    percents = [round(language_count[lang]["count"] / len(repos_with_language) * 100, 2) for lang in names]

    if language_count:
        top_language = max(language_count.keys(), key=lambda x: language_count[x]["count"])
        title_raw = FM.t('I Mostly Code in').replace('%s', '')
        title = f" {title_raw.strip()} {top_language} "
    else:
        title = ""
    return f"{make_list(names=names, texts=texts, percents=percents, title=title, category='repos', col2_name='Repository')}\n\n"
