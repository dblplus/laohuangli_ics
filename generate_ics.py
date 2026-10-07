# -*- coding: utf-8 -*-
"""
老黄历 ICS 日历生成脚本
生成 2026-01-01 至 2028-12-31 的单文件 ICS 订阅日历。
内容：每日宜忌、干支、冲煞、二十四节气、传统节日、吉神方位、时辰吉凶、彭祖百忌、胎神。
数据算法来源：cnlunar 库（离线计算，无需外部 API）。

用法：python generate_ics.py
输出：laohuangli.ics
"""

import datetime
import cnlunar

START_YEAR = 2026
END_YEAR = 2028
OUTPUT_FILE = "laohuangli.ics"
CAL_NAME = "老黄历"
UID_DOMAIN = "laohuangli"

# 十二时辰对应现代时间区间
SHICHEN_HOURS = [
    "23:00-01:00", "01:00-03:00", "03:00-05:00", "05:00-07:00",
    "07:00-09:00", "09:00-11:00", "11:00-13:00", "13:00-15:00",
    "15:00-17:00", "17:00-19:00", "19:00-21:00", "21:00-23:00",
]
DIZHI = "子丑寅卯辰巳午未申酉戌亥"


def ics_escape(text: str) -> str:
    """按 RFC 5545 转义 TEXT 类型属性值。"""
    return (
        str(text)
        .replace("\\", "\\\\")
        .replace(";", "\\;")
        .replace(",", "\\,")
        .replace("\n", "\\n")
    )


def fold_line(line: str) -> str:
    """按 RFC 5545 将行折叠为不超过 75 字节的物理行（UTF-8 安全断行）。"""
    encoded = line.encode("utf-8")
    if len(encoded) <= 75:
        return line
    parts = []
    current = ""
    current_len = 0
    limit = 75
    for ch in line:
        ch_len = len(ch.encode("utf-8"))
        if current_len + ch_len > limit:
            parts.append(current)
            current = " " + ch  # 续行以单个空格开头
            current_len = 1 + ch_len
            limit = 75
        else:
            current += ch
            current_len += ch_len
    parts.append(current)
    return "\r\n".join(parts)


def build_event(day: datetime.date) -> str:
    """为单个公历日期生成全天 VEVENT。"""
    lunar = cnlunar.Lunar(
        datetime.datetime(day.year, day.month, day.day), godType="8char"
    )

    # --- 基础信息 ---
    lunar_md = f"{lunar.lunarMonthCn}{lunar.lunarDayCn}"          # 例：正月初一
    ganzhi = f"{lunar.year8Char}年 {lunar.month8Char}月 {lunar.day8Char}日"
    clash = lunar.chineseZodiacClash                              # 例：狗日冲龙
    zodiac = lunar.chineseYearZodiac                              # 生肖
    good = "、".join(lunar.goodThing) or "无"
    bad = "、".join(lunar.badThing) or "无"
    lucky_dirs = "，".join(lunar.get_luckyGodsDirection())        # 吉神方位
    good_gods = "、".join(lunar.goodGodName)
    bad_gods = "、".join(lunar.badGodName)
    peng_taboo = lunar.get_pengTaboo().replace(",", "；")         # 彭祖百忌
    fetal_god = lunar.get_fetalGod()                              # 胎神
    officer = f"{lunar.today12DayOfficer}日（{lunar.today12DayGod}）"  # 建除十二神
    star28 = lunar.today28Star                                    # 二十八宿

    # 时辰吉凶（取前 12 项，第 13 项为次日子时）
    lucky_list = lunar.get_twohourLuckyList()
    twohour_ganzhi = lunar.twohour8CharList
    twohour = "　".join(
        f"{DIZHI[i]}时({twohour_ganzhi[i]}){lucky_list[i]}" for i in range(12)
    )

    # 节气
    solar_term = lunar.todaySolarTerms if lunar.todaySolarTerms != "无" else ""

    # 传统节日（法定 + 其他公历节日 + 农历节日）
    festivals = []
    for h in (lunar.get_legalHolidays(), lunar.get_otherHolidays(),
              lunar.get_otherLunarHolidays()):
        if h:
            festivals.extend(x for x in str(h).split() if x)
    festival_str = "、".join(dict.fromkeys(festivals))  # 去重保序

    # --- SUMMARY（日历列表页可见，保持精简）---
    title_parts = []
    if solar_term:
        title_parts.append(f"【{solar_term}】")
    if festival_str:
        title_parts.append(f"【{festival_str}】")
    title_parts.append(f"{lunar_md} {lunar.day8Char}日")
    title_parts.append(f"冲{lunar.zodiacLose}")
    good_short = "、".join(lunar.goodThing[:6]) or "无"
    bad_short = "、".join(lunar.badThing[:6]) or "无"
    title_parts.append(f"宜:{good_short}")
    title_parts.append(f"忌:{bad_short}")
    summary = " ".join(title_parts)

    # --- DESCRIPTION（完整详情）---
    desc_lines = [
        f"农历：{lunar.lunarYearCn}年{lunar_md}（{zodiac}年）",
        f"干支：{ganzhi}",
        f"冲煞：{clash}　不利生肖：{lunar.zodiacLose}",
        f"宜：{good}",
        f"忌：{bad}",
        f"吉神方位：{lucky_dirs}",
        f"吉神宜趋：{good_gods}",
        f"凶神宜忌：{bad_gods}",
        f"时辰吉凶：{twohour}",
        f"彭祖百忌：{peng_taboo}",
        f"胎神占方：{fetal_god}",
        f"建除十二神：{officer}　二十八宿：{star28}",
        f"今日等级：{lunar.todayLevelName}",
    ]
    if solar_term:
        desc_lines.insert(0, f"节气：{solar_term}")
    if festival_str:
        desc_lines.insert(0 if not solar_term else 1, f"节日：{festival_str}")
    description = "\n".join(desc_lines)

    dtstart = day.strftime("%Y%m%d")
    dtend = (day + datetime.timedelta(days=1)).strftime("%Y%m%d")
    dtstamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    uid = f"{dtstart}@{UID_DOMAIN}"

    lines = [
        "BEGIN:VEVENT",
        f"UID:{uid}",
        f"DTSTAMP:{dtstamp}",
        f"DTSTART;VALUE=DATE:{dtstart}",
        f"DTEND;VALUE=DATE:{dtend}",
        f"SUMMARY:{ics_escape(summary)}",
        f"DESCRIPTION:{ics_escape(description)}",
        "TRANSP:TRANSPARENT",
        "END:VEVENT",
    ]
    return "\r\n".join(fold_line(l) for l in lines)


def main():
    start = datetime.date(START_YEAR, 1, 1)
    end = datetime.date(END_YEAR, 12, 31)
    days = (end - start).days + 1

    header = "\r\n".join([
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//laohuangli//CN Lunar Almanac//ZH-CN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        fold_line(f"X-WR-CALNAME:{ics_escape(CAL_NAME)}"),
        fold_line(f"X-WR-CALDESC:{ics_escape(f'{START_YEAR}-{END_YEAR} 年老黄历：每日宜忌、干支、冲煞、节气、节日、吉神方位、时辰吉凶')}"),
        "X-WR-TIMEZONE:Asia/Shanghai",
        "REFRESH-INTERVAL;VALUE=DURATION:P7D",
        "X-PUBLISHED-TTL:P7D",
    ])

    events = []
    for i in range(days):
        events.append(build_event(start + datetime.timedelta(days=i)))
        if (i + 1) % 365 == 0:
            print(f"进度：{i + 1}/{days} 天")

    content = header + "\r\n" + "\r\n".join(events) + "\r\nEND:VCALENDAR\r\n"
    with open(OUTPUT_FILE, "w", encoding="utf-8", newline="") as f:
        f.write(content)
    print(f"完成：{OUTPUT_FILE}（{days} 个事件）")


if __name__ == "__main__":
    main()
