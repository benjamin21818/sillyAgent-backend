---
name: "amap-maps-schema-personal-map"
description: "行程规划地图唤醒。用户需要生成高德地图展示链接时调用。"
---

# 行程规划地图唤醒

将行程规划结果组装为高德地图小程序打开链接。

## MCP 工具名称

maps_schema_personal_map

## 关键词

- 行程规划
- 行程地图
- 地图链接
- 唤醒地图
- 高德地图
- 路线展示
- 行程单
- 旅行计划

## 触发时机

- 生成行程规划地图链接
- 在高德地图展示行程

## 使用示例

```json
{
  "orgName": "周末行程",
  "lineList": [
    {
      "title": "第一天",
      "pointInfoList": [
        { "name": "天安门", "lon": 116.397, "lat": 39.908, "poiId": "B000A7BD6C" }
      ]
    }
  ]
}
```
