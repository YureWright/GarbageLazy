# 硬件连接图（ESP32-P4-WIFI + 4 舵机）

## 连接图

```mermaid
flowchart LR
    subgraph PC[电脑]
        USB[USB 口 COM9]
    end

    subgraph BRD[开发板 ESP32-P4-WIFI]
        CH343[CH343 串口芯片]
        P4[ESP32-P4 芯片]
        C6[ESP32-C6 WiFi 模组<br/>SDIO 连接]
        J37[GPIO 37 TX]
        J38[GPIO 38 RX]
        G4[GPIO 4]
        G20[GPIO 20]
        G29[GPIO 29]
        G48[GPIO 48]
        GND1[GND]
    end

    subgraph PWR[外部 5V 电源]
        VCC[VCC 5V]
        GNDP[GND]
    end

    subgraph SERVO[舵机组]
        S1[舵机 1]
        S2[舵机 2]
        S3[舵机 3]
        S4[舵机 4]
    end

    USB -- "USB 线" --> CH343
    CH343 -- "TX → GPIO38 (RX)" --> J38
    J37 -- "TX → CH343 RX" --> CH343

    G4 -- "信号线" --> S1
    G20 -- "信号线" --> S2
    G29 -- "信号线" --> S3
    G48 -- "信号线" --> S4

    VCC -- "红线 5V" --> S1
    VCC -- "红线 5V" --> S2
    VCC -- "红线 5V" --> S3
    VCC -- "红线 5V" --> S4

    GNDP -- "棕线 GND" --> S1
    GNDP -- "棕线 GND" --> S2
    GNDP -- "棕线 GND" --> S3
    GNDP -- "棕线 GND" --> S4

    GND1 -. "共地线（必须有）" .-> GNDP
    GND1 -. "共地线（必须有）" .-> S1

    style J38 fill:#f88,stroke:#c00
    style CH343 fill:#f88,stroke:#c00
    style GND1 fill:#ff8,stroke:#aa0
    style GNDP fill:#ff8,stroke:#aa0
```

## 检查清单

| # | 连接 | 状态 |
|---|------|------|
| 1 | USB 线：电脑 COM9 ↔ 开发板 CH343 | ⚠️ 重点检查：接触不良 |
| 2 | CH343 TX → GPIO 38（RX 接收命令） | ⚠️ 最大疑点，时通时断 |
| 3 | GPIO 37（TX）→ CH343 RX（回传日志） | ✅ 正常 |
| 4 | GPIO 4/20/29/48 → 舵机 1/2/3/4 信号线 | ✅ 已确认引脚覆盖 |
| 5 | 外部电源 VCC → 4 个舵机红/橙线 | ✅ 正常 |
| 6 | 外部电源 GND → 舵机棕/黑线 | ✅ 正常 |
| 7 | 共地：开发板 GND ↔ 外部电源 GND | ✅ 已补 |

## 故障排查记录

- 现象：命令无回显、舵机延迟动作、碰板子后舵机连动数下
- 判断：命令链路（电脑 → GPIO 38）接触不良，时通时断
- 舵机、供电、共地、PWM 输出均验证正常
