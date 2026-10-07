# 老黄历 ICS 日历订阅（2026–2028）

单文件老黄历订阅日历，涵盖 **2026-01-01 至 2028-12-31** 共 1096 天。
每日一条全天事件，包含：**每日宜忌、干支、冲煞、二十四节气、传统节日、吉神方位、时辰吉凶**（另附彭祖百忌、胎神占方、建除十二神、二十八宿）。

数据由 [cnlunar](https://github.com/OPN48/cnLunar) 库离线算法生成，格式遵循 RFC 5545，参考 [oooldtoy/chinese_calender](https://github.com/oooldtoy/chinese_calender) 的订阅模式整合为单文件。

## 一、文件说明

| 文件 | 说明 |
|------|------|
| `laohuangli.ics` | 日历订阅文件（约 1.9MB，1096 个事件） |
| `generate_ics.py` | 生成脚本（Python 3，依赖 `cnlunar`） |

## 二、iPhone 订阅方法（推荐，可联网自动更新）

1. 获取订阅地址（raw URL）：

   ```
   https://raw.githubusercontent.com/dblplus/laohuangli_ics/main/laohuangli.ics
   ```

2. iPhone 操作路径：
   **设置 → 日历 → 账户 → 添加账户 → 其他 → 添加已订阅日历**
3. 粘贴上述 URL → 下一步 → 保存（描述可填「老黄历」）。
4. 打开日历 App，在「日历」列表中勾选「老黄历」，点任意日期即可看到当日黄历事件；点进事件查看完整宜忌详情。
5. 验证同步：检查 2026-02-17 应显示「【春节】 正月大初一 壬戌日 冲龙 …」；节气日如 2026-02-04 应显示「【立春】」。

> 若订阅后未立即显示：日历 App → 下拉刷新，或在 设置 → 日历 → 账户 → 已订阅日历 中确认「获取」频率。

## 三、手动导入方式（不订阅，仅一次性导入）

1. 在 iPhone 上直接打开 raw URL（或从 GitHub 仓库页面下载 `laohuangli.ics`）。
2. 用 Safari 下载后点按文件 →「添加到日历」即可导入全部事件。

> 手动导入为静态快照，后续仓库更新不会同步；订阅方式才会自动更新。

## 四、更新与再生成

农历数据为确定性算法，**2028 年底前无需更新**。到期前扩展覆盖范围：

```bash
pip install cnlunar
# 修改 generate_ics.py 顶部 START_YEAR / END_YEAR
python generate_ics.py
git add laohuangli.ics && git commit -m "扩展日历覆盖范围" && git push
```

iPhone 端按订阅刷新周期（文件头声明 7 天 TTL）自动拉取新版本。

## 五、ICS 关键字段说明

| 字段 | 内容 |
|------|------|
| `SUMMARY` | 节日/节气标签 + 农历月日 + 日干支 + 冲生肖 + 宜忌摘要（各取前 6 项） |
| `DESCRIPTION` | 完整详情：农历、干支、冲煞、宜、忌、吉神方位、吉神宜趋、凶神宜忌、十二时辰吉凶、彭祖百忌、胎神、建除十二神、二十八宿、今日等级 |
| `DTSTART/DTEND` | 全天事件（`VALUE=DATE`，DTEND 为次日） |
| `UID` | `YYYYMMDD@laohuangli`，全局唯一且稳定 |
| `TRANSP:TRANSPARENT` | 全天事件不占用「忙碌」状态 |
| `REFRESH-INTERVAL` / `X-PUBLISHED-TTL` | 声明 7 天刷新周期，供订阅客户端参考 |
