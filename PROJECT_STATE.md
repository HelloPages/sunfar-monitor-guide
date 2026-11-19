# 順發通路三星螢幕講義｜目前狀態

更新：2026-11-19（台北）。

- 正式入口為 https://hellopages.github.io/sunfar-monitor-guide/ 。獨立部署於HelloPages/sunfar-monitor-guide，GitHub Pages讀取權威主線 `main:/docs`。
- 資料範圍是順發V12墊板14個銷售配置、12個完整螢幕型號。S32FM703UC分為FollowMe、FollowMe Pro及白色M7單機。規格顯示「2K QHD」與「4K UHD」。
- 機款速查、六組需求、14份門市話術及示範、10題練習及規格小抄。公開價格只用三星上市新聞稿中對應系列及尺寸的建議售價，未列公告價的條目提示洽詢門市。
- `specs.json` 為核對後的公開規格，`content.json` 為講義內容，`ASSETS.md` 為圖片來源。編修後執行 `python build.py`，正式頁面測試以 `python qa_browser.py --url https://hellopages.github.io/sunfar-monitor-guide/` 執行。
- QA證據留在本機 `qa/local` 和 `qa/live`。390×844、1280×720、1440×900採Chrome驗收，涵蓋切換、搜尋、跳轉、展開規格、複製、作答及14張圖。手機測試是Chrome視窗模擬。
- 高雄店講義與V12印刷原稿屬各自的專案，本案獨立維護。
