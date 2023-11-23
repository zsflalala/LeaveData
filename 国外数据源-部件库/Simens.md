# [西门子](https://mall.siemens.com.cn/pcweb/listSearch?frontCategoryUuid=0185a43ed3c54bd9ad1625a611b72f5f&lvUuid1=8714645080b64156be820f889ae8ca45&lvUuid2=1ed3a606d40146778db487a5fd1f8fff&keyword=)

## 获取一级分类和二级分类的skuNo

1. `https://mall.siemens.com.cn`网页`js`源码中`var compData = {}`中包括所有一级类目、二级类目和三级类目的`uuid`

2. 需要一级类目的`uuid`当作`url = 'https://mall.siemens.com.cn/front/productlist/search'`的`post`请求的请求体，请求体data如下：

   ```python
   data = {"nowPage":1,
   		"pageShow":4800,
   		"specList":[],
           "sortName":"",
           "sortType":"asc",
           "originalPriceStart":"",
           "originalPriceEnd":"",
           "keyword":None,
           "frontCategoryUuid":"8714645080b64156be820f889ae8ca45",
           "contentUuid":"",
           "contentType":"",
           "isAsp":"0"
           }
   ```

   其中`pageShow`一次性最多请求5000条数据，`frontCategoryUuid`就是一级类目的`uuid`。

3. `post`的响应包含商品的基本表格信息，以其中一条信息举例如下：

   ```python
   {
         "agentDisCount": 0.0,
         "backCategoryUuid": "99e477d667804c26bc6a4caa9bdb2b43",
         "bigPic": "images/2022/11/01/FILE6a77e5cff1d94b6e8ee3cd7d618b2d86.png",
         "cardStatus": "2",
         "collectFlag": false,
         "coverImage": "",
         "goodsAttrName": "",
         "has3DModel": false,
         "highlight": [
           {
             "backCategoryUuid": "<em class='esclass' style='color:red;'>99e477d667804c26bc6a4caa9bdb2b43</em>"
           }
         ],
         "inWhiteList": "2",
         "inquiryStatus": "1",
         "integral": 0,
         "itemType": "2",
         "itemTypeStr": "期货",
         "logoKey": "images/2021/08/31/FILE7ec070c5557447e5bb6c0b18e5dac3a4.png",
         "minSale": 1,
         "mlfb": "2KJ4511-1HF21-3AQ1-Z",
         "mlfbNum": "2KJ4511-1HF21-3AQ1-ZB23C02C27C47D21G34K01K06L02L75M56P90Y80",
         "mlfbSp": "2KJ4511|2KJ45111HF21|2KJ45111HF213AQ1|2KJ45111HF213AQ1ZB23C02C27C47D21G34K01K06L02L75M56P90Y80|1HF21|1HF213AQ1|1HF213AQ1ZB23C02C27C47D21G34K01K06L02L75M56P90Y80|3AQ1|3AQ1ZB23C02C27C47D21G34K01K06L02L75M56P90Y80|ZB23C02C27C47D21G34K01K06L02L75M56P90Y80",
         "noStockeSale": false,
         "originalPrice": 0.0,
         "productName": "制动器 L80/100 制动器 手动释放 制动器 手动释放位置 2 Bremsanschlussspannung 380-440V AC 安装位置 M1-B 油位观察窗 防护方式 IP55 表面保护 C1 用于 normale 环境污染 7016 无烟煤灰色 Anschlusskasten-Lage 1B 特殊涂装",
         "productType": "1",
         "productUuid": "10011001000000000103798382687003",
         "realSearchSwitch": true,
         "salePrice": "0.00",
         "sales": 0,
         "searchSwitch": true,
         "showAgentDiscount": false,
         "skuNo": "52200080321",
         "smallPic": [],
         "specList": [],
         "stockShowWayStr": "有货"
       }
   ```

   从中可以获得产品名称`productName`，和产品的`skuNo`，并且带有该类目中的总条数`totalNum`。

## 页面数据提取

1. 爬取需要使用 Cookie和Refer

2. 爬取结果存储在`getProductDetailBySkuNo?skuNo=2100000537`包中，`skuNo`是产品的Index，获取的url为`https://mall.siemens.com.cn/front/productdetail/getProductDetailBySkuNo?skuNo=2100000537`，载荷仅有`skuNo`

   1. `basicImageKey`值中的`imgaeKey`键中存储的是产品图片，

   2. 凡是下载的域名前缀均为`https://slc-di-dcj-prod-oss.oss-accelerate.aliyuncs.com/`

   3. `descTabRelModelList`中含有5个`tabName`,分别为`产品详情`,`3D模型`,`产品参数`,`买家必读`,`资料下载`.

      `产品详情`，存储的是前端网页源代码，可以提取出img和video的链接

      `3D模型`，模型地址`url`示例如下：`https://dcj-3dview.siemens.com.cn/?environment=pro&filePath=3D/2022/08/02/FILE4320c88e03c54568a4fbb21679dfa0e9.svlx`

      =>推导出`resourcesUrl`域名前缀为`https://dcj-3dview.siemens.com.cn/?environment=pro&filePath=`，`resourcesUrl`存储的是`filePath`的值

      `产品参数`，分为pdf下载链接和表格内容。`https://slc-di-dcj-prod-oss.oss-accelerate.aliyuncs.com/`+`paramsContent`值即为下载pdf的链接；表格内容在另一个`noSpecAttrDTOList`键中，`attributeName`是Key，`attrValues`中的`valueName`是Value

      `买家必读`，无图片信息

      `资料下载`，含有`dataUrl1`、`dataUrl2`，分别是产品样本，技术参数下载链接后缀

   4. `specAttrDTOList`包含的即为产品页中的基本信息表格

   

   爬取结果示例如下：

   ```json
   {
     "appraiseTotalNum": 0,
     "basicImageKey": "{\"coverImage\":\"\",\"imageKey\":\"images/2023/09/10/FILEfdbde2897d5f4d0a8ef228e0683542d4.png\"}",
     "cardStatus": "2",
     "cateRelCoverImageKey": "images/2022/11/09/FILE57f64908170e4f54ac19eaba08708a19.png",
     "descTabRelModelList": [
       {
         "createOpeTime": "2021-09-14 21:21:00",
         "createOper": "admin",
         "delFlag": 1,
         "describeContent": "<p>\n    <img src=\"https://slc-di-dcj-prod-oss.oss-accelerate.aliyuncs.com/images/2023/07/06/FILE4837c5e3f83b42b9b904f9a5b56e5895.jpg\"/>\n    <video class=\"edui-upload-video  vjs-default-skin                                      video-js\" controls=\"\" preload=\"none\" width=\"788\" height=\"500\" src=\"https://slc-di-dcj-prod-oss.oss-cn-beijing.aliyuncs.com//images/2023/01/31/FILE0a92a64cc6304fe09c4e48ddf6aba8f6.mp4\" data-setup=\"{}\">\n        <source src=\"https://slc-di-dcj-prod-oss.oss-cn-beijing.aliyuncs.com//images/2023/01/31/FILE0a92a64cc6304fe09c4e48ddf6aba8f6.mp4\" type=\"video/mp4\"/>\n    </video>\n</p>\n<p>\n    <img src=\"https://slc-di-dcj-prod-oss.oss-cn-beijing.aliyuncs.com//images/2023/07/06/FILE56976101171443bd97292fad87438a31.png\" title=\"images/2023/07/06/FILE56976101171443bd97292fad87438a31.png\" alt=\"logo详情页_01.png\"/><a href=\"https://ruggedcom-selector.automation.siemens.com/start\"></a><a href=\"http://www.siemens.com.cn/logo\" target=\"_blank\"><img src=\"https://slc-di-dcj-prod-oss.oss-cn-beijing.aliyuncs.com//images/2023/07/06/FILE55da201d6218435fbb8a5238dcb90aba.png\" title=\"images/2023/07/06/FILE55da201d6218435fbb8a5238dcb90aba.png\" alt=\"logo详情页_02.png\"/></a>\n</p>\n<p>\n    <img src=\"https://slc-di-dcj-prod-oss.oss-cn-beijing.aliyuncs.com//images/2023/07/06/FILE6ba71012a5c94af3a31db8ff42448f45.png\" title=\"images/2023/07/06/FILE6ba71012a5c94af3a31db8ff42448f45.png\" alt=\"logo详情页_03.png\"/>\n</p>\n<p>\n    <a href=\"https://www.siemens.com/cn/zh/products/automation/systems/industrial/plc/logo/logo-software.html#LOGOSoftComfort\" target=\"_blank\"><img src=\"https://slc-di-dcj-prod-oss.oss-cn-beijing.aliyuncs.com//images/2023/07/06/FILE969ebbf536db4a6cae9ff4a26e88fb7b.png\" title=\"images/2023/07/06/FILE969ebbf536db4a6cae9ff4a26e88fb7b.png\" alt=\"logo详情页_04.png\"/></a>\n</p>\n<p>\n    <a href=\"https://www.siemens.com/cn/zh/products/automation/systems/industrial/plc/logo/logo-software.html#LOGOSoftComfort\" target=\"_blank\"><img src=\"https://slc-di-dcj-prod-oss.oss-cn-beijing.aliyuncs.com//images/2023/07/06/FILEbed301581b2d4e6db12d2ae58b0c6a69.png\" title=\"images/2023/07/06/FILEbed301581b2d4e6db12d2ae58b0c6a69.png\" alt=\"logo详情页_05.png\"/></a>\n</p>\n<p>\n    <a href=\"https://www.siemens.com/cn/zh/products/automation/systems/industrial/plc/logo/logo-software.html#LOGOSoftComfort\" target=\"_blank\"><img src=\"https://slc-di-dcj-prod-oss.oss-cn-beijing.aliyuncs.com//images/2023/07/06/FILE41bb3c4dec1d4c289764bdf8ff5ca952.png\" title=\"images/2023/07/06/FILE41bb3c4dec1d4c289764bdf8ff5ca952.png\" alt=\"logo详情页_06.png\"/></a>\n</p>\n<p>\n    <img src=\"https://slc-di-dcj-prod-oss.oss-cn-beijing.aliyuncs.com//images/2023/07/06/FILEba2b0c1b64624adba6d08ba240707e4e.png\" title=\"images/2023/07/06/FILEba2b0c1b64624adba6d08ba240707e4e.png\" alt=\"logo详情页_07.png\"/>\n</p>",
         "mapCondition": {},
         "opeTime": "2023-09-10 23:40:41",
         "oper": "818bb701afb34e729e2d149b5012235e",
         "plat": "1",
         "position": 1,
         "productUuid": "11001000000000103687906",
         "sortName": "opeTime",
         "sortType": "desc",
         "tabName": "产品详情",
         "tabType": "1",
         "tabUuid": "5555",
         "uuid": "1fa1130df97b40c48e5cf28de697f7ea",
         "version": 46
       },
       {
         "createOpeTime": "2021-09-14 21:21:00",
         "createOper": "admin",
         "delFlag": 1,
         "mapCondition": {},
         "opeTime": "2021-09-14 21:21:00",
         "oper": "admin",
         "plat": "1",
         "position": 2,
         "productUuid": "11001000000000103687906",
         "resourcesUrl": "3D/2022/08/02/FILE4320c88e03c54568a4fbb21679dfa0e9.svlx",
         "sortName": "opeTime",
         "sortType": "desc",
         "tabName": "3D模型",
         "tabType": "2",
         "tabUuid": "6666",
         "uuid": "ab3503e18f644da6a5ba75b61cee6f01",
         "version": 2
       },
       {
         "createOpeTime": "2021-09-14 21:21:00",
         "createOper": "admin",
         "delFlag": 1,
         "mapCondition": {},
         "opeTime": "2023-09-10 23:40:41",
         "oper": "818bb701afb34e729e2d149b5012235e",
         "paramsContent": "imagesurlsyncpdf/2021/10/26/e9c28c8a160a4704b2c1eb022c9d8985.pdf",
         "plat": "1",
         "position": 3,
         "productUuid": "11001000000000103687906",
         "sortName": "opeTime",
         "sortType": "desc",
         "tabName": "产品参数",
         "tabType": "3",
         "tabUuid": "7777",
         "uuid": "09b0a8ac09e744f2b8c9a7996c491c9f",
         "version": 39
       },
       {
         "delFlag": 1,
         "mapCondition": {},
         "position": 0,
         "sortName": "opeTime",
         "sortType": "desc",
         "tabName": "买家必读",
         "tabType": "6",
         "version": 0
       },
       {
         "createOpeTime": "2021-09-14 21:21:00",
         "createOper": "admin",
         "dataUrl1": "images/2022/01/07/FILE14803f703be84e259df286a6e8a63432.pdf",
         "dataUrl2": "imagesurlsyncpdf/2021/10/26/e9c28c8a160a4704b2c1eb022c9d8985.pdf",
         "delFlag": 1,
         "mapCondition": {},
         "opeTime": "2023-09-10 23:40:41",
         "oper": "818bb701afb34e729e2d149b5012235e",
         "plat": "1",
         "position": 4,
         "productUuid": "11001000000000103687906",
         "sortName": "opeTime",
         "sortType": "desc",
         "tabName": "资料下载",
         "tabType": "4",
         "tabUuid": "8888",
         "uuid": "1ac53a1d10a7468a93a6724ef8af0163",
         "version": 38
       }
     ],
     "favoriteTotalNum": 0,
     "goodGroupDetails": [],
     "goodsAttrName": " PLC主机 LOGO！主机 LOGO! 12/24RCE 10.8-28.8V DC 8 4 4 0",
     "goodsModel": "6ED1052-1MD08-0BA1",
     "goodsStatus": "1",
     "goodsUuid": "11001000000000103687906",
     "hasFavorite": "2",
     "inquiryStatus": "2",
     "integral": 0,
     "itemType": "1",
     "itemTypeStr": "现货",
     "leadTime": 0,
     "logoKey": "images/2021/08/31/FILE7ec070c5557447e5bb6c0b18e5dac3a4.png",
     "minSale": 1,
     "multiIamgeKeyList": [],
     "noSpecAttrDTOList": [
       {
         "attrValues": [
           {
             "position": 0,
             "selectedValue": "2",
             "valueName": "LOGO! 12/24RCE，主机，集成显示面板. 电源/输入/输出: 12/24V DC/继电器， 8DI (4AI)/4DO，内存400个功能块， 可连接扩展模块，集成以太网接口，集成 Web server，数据记录功能， 用户可自定义网页， 标准 microSD 卡，可进行云连接"
           }
         ],
         "attributeName": "产品",
         "attributeUuid": "",
         "position": 0,
         "selectedValue": "2"
       },
       {
         "attrValues": [
           {
             "position": 0,
             "selectedValue": "2",
             "valueName": "6ED1052-1MD08-0BA1"
           }
         ],
         "attributeName": "产品型号",
         "attributeUuid": "",
         "position": 0,
         "selectedValue": "2"
       },
       {
         "attrValues": [
           {
             "position": 0,
             "selectedValue": "2",
             "valueName": "NONE"
           }
         ],
         "attributeName": "AL",
         "attributeUuid": "",
         "position": 0,
         "selectedValue": "2"
       },
       {
         "attrValues": [
           {
             "position": 0,
             "selectedValue": "2",
             "valueName": "NONE"
           }
         ],
         "attributeName": "ECCN",
         "attributeUuid": "",
         "position": 0,
         "selectedValue": "2"
       },
       {
         "attrValues": [
           {
             "position": 0,
             "selectedValue": "2",
             "valueName": "中国"
           }
         ],
         "attributeName": "原产国",
         "attributeUuid": "",
         "position": 0,
         "selectedValue": "2"
       },
       {
         "attrValues": [
           {
             "position": 0,
             "selectedValue": "2",
             "valueName": "P.M300"
           }
         ],
         "attributeName": "生命周期",
         "attributeUuid": "",
         "position": 0,
         "selectedValue": "2"
       },
       {
         "attrValues": [
           {
             "position": 0,
             "selectedValue": "2",
             "valueName": "PLC主机"
           }
         ],
         "attributeName": "产品类型",
         "attributeUuid": "",
         "position": 0,
         "selectedValue": "2"
       },
       {
         "attrValues": [
           {
             "position": 0,
             "selectedValue": "2",
             "valueName": "LOGO！主机"
           }
         ],
         "attributeName": "类型",
         "attributeUuid": "",
         "position": 0,
         "selectedValue": "2"
       },
       {
         "attrValues": [
           {
             "position": 0,
             "selectedValue": "2",
             "valueName": "LOGO! 12/24RCE"
           }
         ],
         "attributeName": "型号",
         "attributeUuid": "",
         "position": 0,
         "selectedValue": "2"
       },
       {
         "attrValues": [
           {
             "position": 0,
             "selectedValue": "2",
             "valueName": "10.8-28.8V DC"
           }
         ],
         "attributeName": "工作电压",
         "attributeUuid": "",
         "position": 0,
         "selectedValue": "2"
       },
       {
         "attrValues": [
           {
             "position": 0,
             "selectedValue": "2",
             "valueName": "8"
           }
         ],
         "attributeName": "数字输入量",
         "attributeUuid": "",
         "position": 0,
         "selectedValue": "2"
       },
       {
         "attrValues": [
           {
             "position": 0,
             "selectedValue": "2",
             "valueName": "4"
           }
         ],
         "attributeName": "数字输出量",
         "attributeUuid": "",
         "position": 0,
         "selectedValue": "2"
       },
       {
         "attrValues": [
           {
             "position": 0,
             "selectedValue": "2",
             "valueName": "4"
           }
         ],
         "attributeName": "模拟输入量",
         "attributeUuid": "",
         "position": 0,
         "selectedValue": "2"
       },
       {
         "attrValues": [
           {
             "position": 0,
             "selectedValue": "2",
             "valueName": "0"
           }
         ],
         "attributeName": "模拟输出量",
         "attributeUuid": "",
         "position": 0,
         "selectedValue": "2"
       },
       {
         "attrShowName": "存储器容量",
         "attrValues": [
           {
             "position": 1,
             "selectedValue": "1",
             "valueName": "8500Byte",
             "valueUuid": "297190b24e614feeba2f7fce6949b52c"
           }
         ],
         "attributeName": "存储器容量",
         "attributeUuid": "ec8625bf49154b03991021349d4b52c4",
         "position": 1,
         "selectedValue": "1",
         "type": "1"
       },
       {
         "attrShowName": "宽度",
         "attrValues": [
           {
             "position": 1,
             "selectedValue": "1",
             "valueName": "71.5mm",
             "valueUuid": "4420e5c3d6db4b82b873fbd959c3d991"
           }
         ],
         "attributeName": "宽度",
         "attributeUuid": "fcf4eb0f7dc54ddbafe807a7423703dd",
         "position": 2,
         "selectedValue": "1",
         "type": "1"
       },
       {
         "attrShowName": "高度",
         "attrValues": [
           {
             "position": 1,
             "selectedValue": "1",
             "valueName": "90mm",
             "valueUuid": "3340bae559da4482b99f46ba29c9c7e5"
           }
         ],
         "attributeName": "高度",
         "attributeUuid": "b271d3972f514f1ca7657055c17a570b",
         "position": 3,
         "selectedValue": "1",
         "type": "1"
       },
       {
         "attrShowName": "深度",
         "attrValues": [
           {
             "position": 1,
             "selectedValue": "1",
             "valueName": "60mm",
             "valueUuid": "fd5b165586704946b2950f5c4fa0d22b"
           }
         ],
         "attributeName": "深度",
         "attributeUuid": "c5727ab026924929ac31e48cc9876b8c",
         "position": 4,
         "selectedValue": "1",
         "type": "1"
       }
     ],
     "platCategoryUuid": "25e3fb45e1204f4686c55b00b529c87f",
     "postage": 15.0,
     "productName": "西门子PLC可编程控制器 LOGO! 8.3 12/24RCE 主机模块 6ED10521MD080BA1",
     "productType": "1",
     "saleTotalNum": 0,
     "sales": 16153,
     "sapNo": "103687906",
     "skuNo": "2100000539",
     "skuUnitNum": "PC",
     "specAttrDTOList": [
       {
         "attrName": "产品类型",
         "attrShowName": "产品类型",
         "attrUuid": "c76b4bb22c504bc7bf65bc54f2e9a194",
         "attrValueName": "PLC主机",
         "attrValuePosition": 1,
         "attrValueUuid": "a1a534ba000747b7ad738a963ba1f4a6",
         "canColor": "2",
         "position": 1
       },
       {
         "attrName": "类型",
         "attrShowName": "类型",
         "attrUuid": "dc0568d49d5346c6816ef045991653d6",
         "attrValueName": "LOGO！主机",
         "attrValuePosition": 2,
         "attrValueUuid": "8c4fee6ed10c48779c51c4a73c3d4018",
         "canColor": "2",
         "position": 1
       },
       {
         "attrName": "型号",
         "attrShowName": "型号",
         "attrUuid": "d3612c450ed543ac99e7f5f2d875c4ad",
         "attrValueName": "LOGO! 12/24RCE",
         "attrValuePosition": 3,
         "attrValueUuid": "88c2895189134a989f876eec39d0612f",
         "canColor": "2",
         "position": 1
       },
       {
         "attrName": "工作电压",
         "attrShowName": "工作电压",
         "attrUuid": "58b39b213b6f4e0e9f774121c041300a",
         "attrValueName": "10.8-28.8V DC",
         "attrValuePosition": 4,
         "attrValueUuid": "4d313348bdd1471c862e0266618c38fd",
         "canColor": "2",
         "position": 1
       },
       {
         "attrName": "数字输入量",
         "attrShowName": "数字输入量",
         "attrUuid": "c29ff9e352aa4ea4bdc9595371fac258",
         "attrValueName": "8",
         "attrValuePosition": 5,
         "attrValueUuid": "ede7a660ba784edcafcd357fc229b19e",
         "canColor": "2",
         "position": 1
       },
       {
         "attrName": "数字输出量",
         "attrShowName": "数字输出量",
         "attrUuid": "b6fb3717b37941ec8f4311ab67cd2540",
         "attrValueName": "4",
         "attrValuePosition": 6,
         "attrValueUuid": "3c4397aea0e944f8ab2eb5cf81debcf8",
         "canColor": "2",
         "position": 1
       },
       {
         "attrName": "模拟输入量",
         "attrShowName": "模拟输入量",
         "attrUuid": "8d98a7c2533740f5a8a21d44bcc5853d",
         "attrValueName": "4",
         "attrValuePosition": 7,
         "attrValueUuid": "a1988afbdd6e45fba899773ee856577d",
         "canColor": "2",
         "position": 1
       },
       {
         "attrName": "模拟输出量",
         "attrShowName": "模拟输出量",
         "attrUuid": "518673259d4f45c0889ca58a8492edb9",
         "attrValueName": "0",
         "attrValuePosition": 8,
         "attrValueUuid": "4789e36adc7d4f039a0f44da2ffbcdce",
         "canColor": "2",
         "position": 1
       }
     ],
     "specAttrList": [
       {
         "attrName": "产品类型",
         "attrShowName": "产品类型",
         "attrUuid": "c76b4bb22c504bc7bf65bc54f2e9a194",
         "attrValues": [
           {
             "position": 1,
             "selectedValue": "2",
             "valueName": "PLC主机",
             "valueUuid": "a1a534ba000747b7ad738a963ba1f4a6"
           }
         ],
         "position": 1
       },
       {
         "attrName": "类型",
         "attrShowName": "类型",
         "attrUuid": "dc0568d49d5346c6816ef045991653d6",
         "attrValues": [
           {
             "position": 2,
             "selectedValue": "2",
             "valueName": "LOGO！主机",
             "valueUuid": "8c4fee6ed10c48779c51c4a73c3d4018"
           }
         ],
         "position": 1
       },
       {
         "attrName": "型号",
         "attrShowName": "型号",
         "attrUuid": "d3612c450ed543ac99e7f5f2d875c4ad",
         "attrValues": [
           {
             "position": 3,
             "selectedValue": "2",
             "valueName": "LOGO! 12/24RCE",
             "valueUuid": "88c2895189134a989f876eec39d0612f"
           }
         ],
         "position": 1
       },
       {
         "attrName": "工作电压",
         "attrShowName": "工作电压",
         "attrUuid": "58b39b213b6f4e0e9f774121c041300a",
         "attrValues": [
           {
             "position": 4,
             "selectedValue": "2",
             "valueName": "10.8-28.8V DC",
             "valueUuid": "4d313348bdd1471c862e0266618c38fd"
           }
         ],
         "position": 1
       },
       {
         "attrName": "数字输入量",
         "attrShowName": "数字输入量",
         "attrUuid": "c29ff9e352aa4ea4bdc9595371fac258",
         "attrValues": [
           {
             "position": 5,
             "selectedValue": "2",
             "valueName": "8",
             "valueUuid": "ede7a660ba784edcafcd357fc229b19e"
           }
         ],
         "position": 1
       },
       {
         "attrName": "数字输出量",
         "attrShowName": "数字输出量",
         "attrUuid": "b6fb3717b37941ec8f4311ab67cd2540",
         "attrValues": [
           {
             "position": 6,
             "selectedValue": "2",
             "valueName": "4",
             "valueUuid": "3c4397aea0e944f8ab2eb5cf81debcf8"
           }
         ],
         "position": 1
       },
       {
         "attrName": "模拟输入量",
         "attrShowName": "模拟输入量",
         "attrUuid": "8d98a7c2533740f5a8a21d44bcc5853d",
         "attrValues": [
           {
             "position": 7,
             "selectedValue": "2",
             "valueName": "4",
             "valueUuid": "a1988afbdd6e45fba899773ee856577d"
           }
         ],
         "position": 1
       },
       {
         "attrName": "模拟输出量",
         "attrShowName": "模拟输出量",
         "attrUuid": "518673259d4f45c0889ca58a8492edb9",
         "attrValues": [
           {
             "position": 8,
             "selectedValue": "2",
             "valueName": "0",
             "valueUuid": "4789e36adc7d4f039a0f44da2ffbcdce"
           }
         ],
         "position": 1
       }
     ],
     "suAttrList": [
       {
         "goodsStatus": "1",
         "skuNo": "2100000539",
         "specAttrDTOList": [
           {
             "attrName": "产品类型",
             "attrShowName": "产品类型",
             "attrUuid": "c76b4bb22c504bc7bf65bc54f2e9a194",
             "attrValueName": "PLC主机",
             "attrValuePosition": 1,
             "attrValueUuid": "a1a534ba000747b7ad738a963ba1f4a6",
             "canColor": "2",
             "position": 1
           },
           {
             "attrName": "类型",
             "attrShowName": "类型",
             "attrUuid": "dc0568d49d5346c6816ef045991653d6",
             "attrValueName": "LOGO！主机",
             "attrValuePosition": 2,
             "attrValueUuid": "8c4fee6ed10c48779c51c4a73c3d4018",
             "canColor": "2",
             "position": 1
           },
           {
             "attrName": "型号",
             "attrShowName": "型号",
             "attrUuid": "d3612c450ed543ac99e7f5f2d875c4ad",
             "attrValueName": "LOGO! 12/24RCE",
             "attrValuePosition": 3,
             "attrValueUuid": "88c2895189134a989f876eec39d0612f",
             "canColor": "2",
             "position": 1
           },
           {
             "attrName": "工作电压",
             "attrShowName": "工作电压",
             "attrUuid": "58b39b213b6f4e0e9f774121c041300a",
             "attrValueName": "10.8-28.8V DC",
             "attrValuePosition": 4,
             "attrValueUuid": "4d313348bdd1471c862e0266618c38fd",
             "canColor": "2",
             "position": 1
           },
           {
             "attrName": "数字输入量",
             "attrShowName": "数字输入量",
             "attrUuid": "c29ff9e352aa4ea4bdc9595371fac258",
             "attrValueName": "8",
             "attrValuePosition": 5,
             "attrValueUuid": "ede7a660ba784edcafcd357fc229b19e",
             "canColor": "2",
             "position": 1
           },
           {
             "attrName": "数字输出量",
             "attrShowName": "数字输出量",
             "attrUuid": "b6fb3717b37941ec8f4311ab67cd2540",
             "attrValueName": "4",
             "attrValuePosition": 6,
             "attrValueUuid": "3c4397aea0e944f8ab2eb5cf81debcf8",
             "canColor": "2",
             "position": 1
           },
           {
             "attrName": "模拟输入量",
             "attrShowName": "模拟输入量",
             "attrUuid": "8d98a7c2533740f5a8a21d44bcc5853d",
             "attrValueName": "4",
             "attrValuePosition": 7,
             "attrValueUuid": "a1988afbdd6e45fba899773ee856577d",
             "canColor": "2",
             "position": 1
           },
           {
             "attrName": "模拟输出量",
             "attrShowName": "模拟输出量",
             "attrUuid": "518673259d4f45c0889ca58a8492edb9",
             "attrValueName": "0",
             "attrValuePosition": 8,
             "attrValueUuid": "4789e36adc7d4f039a0f44da2ffbcdce",
             "canColor": "2",
             "position": 1
           }
         ]
       }
     ],
     "subjectTypeStr": "西门子（中国）有限公司",
     "uuid": "e92056fdfcdd409ca65735f23e377abe",
     "videoKey": "images/2022/11/09/FILEd00e24022a234e5791ba546d38d34e5d.mp4"
   }
   ```


## 数据重新处理

```json
{
      "url": "https://mall.siemens.com.cn/pcweb/detailIndex/52100014613.html",
      "first_type": "联合钜惠",
      "second_type": "",
      "产品名称": "联合钜惠低价 西门子 3VL17081DA330AA0",
      "产品图片": "https://slc-di-dcj-prod-oss.oss-accelerate.aliyuncs.com/imagesurlsync/2021/10/28/O1CN01xF2KSF1T1yjfLL66j_!!2895262323-0-cib.jpg",
      "产品视频": {},
      "基本信息": {
        "注意": "联系客服，立即获取购买机会"
      },
      "产品详情": {
        "image": [
          "https://slc-di-dcj-prod-oss.oss-accelerate.aliyuncs.com/images/2022/07/20/FILE5c9a0abec7124e24aa69dd59eb212313.jpg"
        ],
        "video": []
      },
      "买家必读": "https://slc-di-dcj-prod-oss.oss-cn-beijing.aliyuncs.com//images/2021/11/17/FILEfe3ed29ffe78413492b00e04112236e1.jpg",
      "3D模型": "",
      "产品参数": "https://slc-di-dcj-prod-oss.oss-accelerate.aliyuncs.com/imagesurlsyncpdf/2022/03/12/345116c1d66c4beb92d2dddab1bdc09f.pdf",
      "资料下载": {
        "产品样本": "",
        "技术参数": "https://slc-di-dcj-prod-oss.oss-accelerate.aliyuncs.com/imagesurlsyncpdf/2022/03/12/345116c1d66c4beb92d2dddab1bdc09f.pdf"
      },
      "基本参数": {
        "产品": "清仓钜惠低价 西门子 3VL17081DA330AA0",
        "产品型号": "3VL1708-1DA33-0AA0",
        "注意": "联系客服，立即获取购买机会"
      }
    }
```

处理之后的数据存入crawlab中，`save_item`

## Crawlab运行注意点/疑惑点

1. 主函数要单独封装在函数中，放在`if __name__ == '__main__':`中会重复运行，导致数据冗余

   节点原因，以后先打印数据看看是不是一遍

2. 主机似乎要一直开着，不然数据存入不了数据库

   写快速的方法，循环爬取实在是慢

3. 数据不知如何删除

   不用删了，直接无数据源，提前开好数据去重