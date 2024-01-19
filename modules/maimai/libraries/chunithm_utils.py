import ujson as json
from datetime import datetime

from core.builtins import Plain
from core.utils.http import get_url
from core.utils.image import msgchain2image
from .chunithm_apidata import get_record

SONGS_PER_PAGE = 20

score_to_rank = {
    (0, 499999): "D",
    (500000, 599999): "C",
    (600000, 699999): "B",
    (700000, 799999): "BB",
    (800000, 899999): "BBB",
    (900000, 924999): "A",
    (925000, 949999): "AA",
    (950000, 974999): "AAA",
    (975000, 989999): "S",
    (990000, 999999): "S+",
    (1000000, 1004999): "SS",
    (1005000, 1007499): "SS+",
    (1007500, 1008999): "SSS",
    (1009000, 1010000): "SSS+",
}

combo_conversion = {
    "fullcombo": "FC",
    "alljustice": "AJ"
}


def get_diff(diff):
    diff_label = ['Basic', 'Advanced', 'Expert', 'Master', 'Ultima']
    diff_label_abbr = ['bas', 'adv', 'exp', 'mas', 'ult']
    diff_label_zhs = ['绿', '黄', '红', '紫', '黑']
    diff_label_zht = ['綠', '黃', '紅']

    diff = diff.lower()
    diff_label_lower = [label.lower() for label in diff_label]

    if diff in diff_label_zhs:
        level = diff_label_zhs.index(diff)
    elif diff in diff_label_zht:
        level = diff_label_zht.index(diff)
    elif diff in diff_label_abbr:
        level = diff_label_abbr.index(diff)
    elif diff in diff_label_lower:
        level = diff_label_lower.index(diff)
    else:
        level = None
    return level
    

async def generate_best30_text(msg, payload):
    data = await get_record(msg, payload)
    b30_records = data["records"]["b30"]
    r10_records = data["records"]["r10"]
    
    html = "<style>pre { font-size: 15px; }</style><div style='margin-left: 30px; margin-right: 20px;'>\n"
    html += f"{msg.locale.t('chunithm.message.b30.text_prompt', user=data['username'], rating=round(data['rating'], 2))}\n<pre>"
    html += "Best30\n"
    for idx, chart in enumerate(b30_records, start=1):
        level = ''.join(filter(str.isalpha, chart["level_label"]))[:3].upper()
        rank = next(
                rank for interval, rank in score_to_rank.items() if interval[0] <= chart["score"] < interval[1]  # 根据成绩获得等级
            )
        title = chart["title"]
        title = title[:17] + '...' if len(title) > 20 else title
        line = "#{:<2} {:>4} {:<3} {:>7} {:<4} {:<2} {:>4}->{:<5.2f} {:<20}\n".format(
            idx,
            chart["mid"],
            level,
            chart["score"],
            rank,
            combo_conversion.get(chart["fc"], ""),
            chart["ds"],
            chart["ra"],
            title
        )
        html += line
    html += "Recent10\n"
    for idx, chart in enumerate(r10_records, start=1):
        level = ''.join(filter(str.isalpha, chart["level_label"]))[:3].upper()
        rank = next(
                rank for interval, rank in score_to_rank.items() if interval[0] <= chart["score"] < interval[1]  # 根据成绩获得等级
            )
        title = chart["title"]
        title = title[:17] + '...' if len(title) > 20 else title
        line = "#{:<2} {:>4} {:<3} {:>7} {:<4} {:<2} {:>4}->{:<5.2f} {:<20}\n".format(
            idx,
            chart["mid"],
            level,
            chart["score"],
            rank,
            combo_conversion.get(chart["fc"], ""),
            chart["ds"],
            chart["ra"],
            title
        )
        html += line
    html += "</pre>"
    time = msg.ts2strftime(datetime.now().timestamp(), iso=True, timezone=False)
    html += f"<p style='font-size: 10px; text-align: right;'>CHUNITHM Best30 Generator Beta\n{time}·Generated by Teahouse Studios \"Akaribot\"</p>"
    html += "</div>"
    
    img = await msgchain2image([Plain(html)])
    if img:
        return img
    else:
        await msg.finish(msg.locale.t("error.config.webrender.invalid"))