# 順發三星螢幕門市銷售講義

正式入口：https://www.funfun.idv.tw/demo/202611-SF/ （2026/11/23 依 Sam 指定移至此入口）。

LINE外開瀏覽器短網址：https://spoo.me/31Hk2Zx ，導向正式入口並保留 openExternalBrowser=1。

頁首主標題以「順發三星螢幕」開頭；頂部只保留機款、選機、練習導覽。練習答對使用藍字，答錯使用紅字，兩者皆顯示該題解釋；下一題與重新作答清除上一題的配色。

共14個銷售配置、12個完整螢幕型號。機款範圍與規格取自順發V12規格墊板，操作與教學架構取自高雄順發線上講義。順發各門市可使用，實際品項、販售組合、價格及活動依門市確認。

## 維護

- `specs.json` 保存核對後的機款、規格與台灣三星來源。以 `item_id` 辨認完整銷售配置，S32FM703UC的桌上白色單機、FollowMe及FollowMe Pro分開。
- `content.json` 是情境、講解、題目及官方價格資料；價格依來源分為建議售價、官網原價、官網標準價格與待確認，完整核對見 `PRICE_SOURCES.md`。促銷價不能當作建議售價，單機價不能當成移動架套組價。
- `docs/images/` 存放可公開的低解析商品圖及情境圖，來源見 `ASSETS.md`。照片應比對到完整型號、顏色與組合。
- `py -3.11 build.py` 重建 `docs/index.html`。開啟 `py -3.11 -m http.server 8768 --directory docs` 可測試，亦可印出機款與規格。
- 版本來源沿用 `HelloPages/sunfar-monitor-guide` 的 `main:/docs`。正式交付為 Funfun 的 `/public_html/demo/202611-SF`；只上傳 `docs` 內的公開 HTML、CSS、JS、robots.txt 及 images/*.webp，素材先傳、index.html 最後傳，發布後以 FTP/HTTPS 讀回比對 SHA-256。既有 GitHub Pages 設定保留，正式交付使用上述 Funfun 網址。原始墊板PDF、門市成交價、原圖、3D模型、私人規範與驗收截圖皆留在原工作環境。
- 順發通路門市教育訓練素材。產品影像及規格來源為台灣三星；FollowMe圖片用對應組合情境示意。網站無登入及結果上傳機制。

## 2026/11/23 更新與維護

- 共用 FTP TLS 連線沿用 `D:\00_程式\20261015_samsungtw-monitor\tools\hosting.py` 的 `connect()`，由本機既有設定讀取憑證，不把帳密寫入專案。
- 不執行高雄順發舊專案的 `deploy.py`、`update_index.py`，它們綁定其他站點。僅維護使用者指定的 `/public_html/demo/202611-SF`，保留大小寫。
- 瀏覽器驗收沿用 `py -3.11 qa_browser.py`；正式站可執行 `py -3.11 qa_browser.py --url https://www.funfun.idv.tw/demo/202611-SF/`。本輪另實際點選答對、答錯與重新作答，檢查配色及完整解釋；證據存放 `qa/20261123/`。

## 2026/11/23 官方價格與型號連結

- 14個速查型號及14個機款卡片型號都可另開對應台灣三星產品頁；速查照片與品名仍定位至教學。兩種連結為相鄰元素，不能巢狀。
- 11個銷售配置顯示有對應官方來源的價格。FollowMe Pro 32/43吋的套組建議售價保留待確認，另列有官方公告的螢幕單機參考並緊接註明不含Pro氣壓架；S3官網只查得促銷金額，建議售價待確認。
- 價格依 `item_id` 保存，不以共用面板型號合併。白色M7桌上單機10,990元與官網FollowMe托盤立架組13,990元分開。
- `price_checked_at` 為實際查核日期；更新價格時重查官方頁面的原價與促銷欄位，並更新 `PRICE_SOURCES.md`。個別證據與這輪驗收存於 `qa/20261123-prices/`。

- Funfun靜態樣式有7天快取，生成器對CSS及JS網址加入各自檔案SHA-256前12碼作為版本參數，檔案變更後可取得新版本；不需叫使用者清除快取。
