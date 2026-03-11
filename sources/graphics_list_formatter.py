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


def make_list(data: List = None, names: List[str] = None, texts: List[str] = None, percents: List[float] = None, top_num: int = 5, sort: bool = True, title: str = "") -> str:
    """
    Make list of HTML tables displaying progress bars with supportive info.
    Each row has the following structure: [name of the measure] [quantity description (with words)] [progress bar] [total percentage].
    """
    if data is not None:
        names = [value for item in data for key, value in item.items() if key == "name"] if names is None else names
        texts = [value for item in data for key, value in item.items() if key == "text"] if texts is None else texts
        percents = [value for item in data for key, value in item.items() if key == "percent"] if percents is None else percents

    data_tuples = list(zip(names, texts, percents))
    top_data = sorted(data_tuples[:top_num], key=lambda record: record[2], reverse=True) if sort else data_tuples[:top_num]
    
    table_html = f'''<table width="100%">
  <thead>
    <tr>
      <th colspan="3" align="center">💬 {title if title else "Statistics"}</th>
    </tr>
    <tr>
      <th align="left">Name</th>
      <th align="center">Time Spent / Quantity</th>
      <th align="left">Progress</th>
    </tr>
  </thead>
  <tbody>'''

    for n, t, p in top_data:
        # Generate color based on percentage
        color = "3fb950" if p > 30 else ("fdb660" if p > 15 else "ce4242")
        
        # Format the name: Try to get a devicon, otherwise just the name
        icon_url = f"https://raw.githubusercontent.com/devicons/devicon/master/icons/{str(n).lower().replace(' ', '')}/{str(n).lower().replace(' ', '')}-original.svg"
        name_html = f'<img src="{icon_url}" width="16" height="16" style="vertical-align: middle;" onerror="this.style.display=\'none\'"> {n}'
        
        row_html = f'''
    <tr>
      <td>{name_html}</td>
      <td align="center">{t}</td>
      <td><img src="https://geps.dev/progress/{int(p)}?color={color}" alt="{p:05.2f}%" /></td>
    </tr>'''
        table_html += row_html

    table_html += '''
  </tbody>
</table>'''
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
        stats += f"**{title}** \n\n{make_list(names=dt_names, texts=dt_texts, percents=dt_percents, top_num=7, sort=False, title='Day/Night Commits')}\n"

    if EM.SHOW_DAYS_OF_WEEK:
        wd_names = [FM.t(week_day) for week_day in WEEK_DAY_NAMES]
        wd_texts = [f"{week_day} commits" for week_day in week_days]
        wd_percents = [0 if sum_week == 0 else round((week_day / sum_week) * 100, 2) for week_day in week_days]
        title = FM.t("I am Most Productive on") % wd_names[wd_percents.index(max(wd_percents))]
        stats += f"📅 **{title}** \n\n{make_list(names=wd_names, texts=wd_texts, percents=wd_percents, top_num=7, sort=False, title='Day of Week Commits')}\n"

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
        title = f"**{FM.t('I Mostly Code in') % top_language}** \n\n"
    else:
        title = ""
    return f"{title}{make_list(names=names, texts=texts, percents=percents, title='Repos per Language')}\n\n"
