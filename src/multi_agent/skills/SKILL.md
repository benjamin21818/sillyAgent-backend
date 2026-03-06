---
name: "skills-index"
description: "所有能调用的mcp服务端的工具列表和说明"
---

# 技能目录入口说明

本文件用于说明所有mcp服务器中能调用的工具名称


## 技能清单

- web-search：网页搜索（MCP 工具：search_web）
- amap-maps-direction-bicycling：骑行路线规划（MCP 工具：maps_direction_bicycling）
- amap-maps-direction-driving：驾车路线规划（MCP 工具：maps_direction_driving）
- amap-maps-direction-transit：公共交通规划（MCP 工具：maps_direction_transit_integrated）
- amap-maps-direction-walking：步行路线规划（MCP 工具：maps_direction_walking）
- amap-maps-distance：距离测量（MCP 工具：maps_distance）
- amap-maps-geo：地址转坐标（MCP 工具：maps_geo）
- amap-maps-regeocode：坐标转地址（MCP 工具：maps_regeocode）
- amap-maps-ip-location：IP 定位（MCP 工具：maps_ip_location）
- amap-maps-schema-personal-map：行程规划地图唤醒（MCP 工具：maps_schema_personal_map）
- amap-maps-around-search：周边搜索（MCP 工具：maps_around_search）
- amap-maps-search-detail：POI 详情查询（MCP 工具：maps_search_detail）
- amap-maps-text-search：关键词搜索（MCP 工具：maps_text_search）
- amap-maps-schema-navi：导航唤醒链接（MCP 工具：maps_schema_navi）
- amap-maps-schema-take-taxi：打车唤醒链接（MCP 工具：maps_schema_take_taxi）
- amap-maps-weather：天气查询（MCP 工具：maps_weather）


## 目录结构

每个技能必须放在独立的子目录中，结构如下：

```
skills/
  <skill-name>/
    SKILL.md
```

