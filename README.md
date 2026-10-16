# What to Eat!

不知道吃什麼？輸入你在的地標，選距離和料理類別，從自己的 Google Maps 收藏清單裡抽一家。

純靜態網頁（HTML / CSS / JavaScript ES modules），沒有後端，也不需要任何 API 金鑰。

## 功能

- 輸入地標或地址（例如「松仁路7號」）、點常用捷運站，或使用手機定位
- 距離 500 公尺～50 公里；料理類別可多選（咖啡、麵食、日式、火鍋…）；收藏清單可多選
- 「幫我決定一家」：同一輪不重複，抽完才重新洗牌
- 可加到手機主畫面（PWA manifest + 圖示）

## 技術選擇與取捨

- **不用 Google Places API**：改用 Google Maps 清單匯出的座標，自己算距離（Haversine 直線距離）。代價是沒有評分與營業時間資料，所以沒有「4.3 分以上」篩選。
- **地標查詢用 Photon / OpenStreetMap**：免金鑰。踩到的坑：Photon 依瀏覽器語言回傳，英文瀏覽器會得到英文地址，所以請求時固定 `lang=default` 並過濾沒有中文的結果；它也要求「路」與門牌數字間有空格才找得到，因此送出前自動補空格（`fixAddressQuery`）。
- **分類**：依店名關鍵字規則做初步分類，再手動修正少數，可能有誤；無法判斷的標為「待分類」，不參與預設抽選。

## 結構

```
dist/            網站本體（部署這個資料夾）
  core.mjs       距離計算、篩選、不重複抽選（純函式，可單獨測試）
  app.mjs        介面與事件
  data/          places.json（收藏）、landmarks.json（常用地標）
tests/           node tests/core.test.mjs
import-list*.py  匯入 Google Maps 清單並分類
```

## 本機執行與測試

```
python3 -m http.server 8765 -d dist
node tests/core.test.mjs
```

地標資料 © OpenStreetMap contributors · Photon
