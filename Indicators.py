"""
DT-Box
Pavel Chigirev, pavelchigirev.com, 2023-2024
See LICENSE.txt for details
"""

ind_symbols = [
    "EURUSD",
    "USDJPY",
    "GBPUSD",
    "AUDUSD",
    "USDCAD",
    "USDCHF",
    "EURGBP"
]

ind_periods = [
    "PERIOD_CURRENT",
    "PERIOD_M1",
    "PERIOD_M2",
    "PERIOD_M3",
    "PERIOD_M4",
    "PERIOD_M5",
    "PERIOD_M6",
    "PERIOD_M10",
    "PERIOD_M12",
    "PERIOD_M15",
    "PERIOD_M20",
    "PERIOD_M30",
    "PERIOD_H1",
    "PERIOD_H2",
    "PERIOD_H3",
    "PERIOD_H4",
    "PERIOD_H6",
    "PERIOD_H8",
    "PERIOD_H12",
    "PERIOD_D1",
    "PERIOD_W1",
    "PERIOD_MN1"]

ind_app_price = [
    "PRICE_CLOSE",
    "PRICE_OPEN",
    "PRICE_HIGH",
    "PRICE_LOW",
    "PRICE_MEDIAN",
    "PRICE_TYPICAL",
    "PRICE_WEIGHTED"]

ma_modes = [
    "MODE_SMA",
    "MODE_EMA",
    "MODE_SMMA",
    "MODE_LWMA"]

so_prices = [
    "STO_LOWHIGH",
    "STO_CLOSECLOSE"]

ind_types = [
    "Moving Average (MA)", 
    "Commodity Channel Index (CCI)",
    "Bollinger Bands (BB)", 
    "MACD", 
    "Standard Deviation (SD)",
    "Average True Range (ATR)",
    "Stochastic Oscillator (SO)", 
    "Parabolic SAR",
    "Triple EMA (TEMA)",
    "Adaptive Moving Average (AMA)"]

ma_params = ["Period", "Shift", "Mode", "AppliedPrice", "Color"]
ma_param_types = ["int", "int", ma_modes, ind_app_price, "color"]
ma_def_values = ["20", "0", "MODE_SMA", "PRICE_CLOSE", "#ffff80"]

cci_params =  ["Period", "AppliedPrice", "Color"]
cci_param_types = ["int", ind_app_price, "color"]
cci_def_values =  ["20", "PRICE_CLOSE", "#ffff80"]

bb_params = ["Period", "Shift", "Deviations", "AppliedPrice", "Color"]
bb_param_types = ["int", "int", "double", ind_app_price, "color"]
bb_def_values = ["20", "0", "2.0", "PRICE_CLOSE", "#ffff80"]

macd_params = ["FastEMA", "SlowEMA", "SignalSMA", "AppliedPrice", "Color1", "Color2"]
macd_param_types = ["int", "int", "int", ind_app_price, "color", "color"]
macd_def_values = ["12", "26", "9", "PRICE_CLOSE", "#c0c0c0", "#ffff80"]

sd_params = ["Period", "Shift", "Mode", "AppliedPrice", "Color"]
sd_param_types =["int", "int", ma_modes, ind_app_price, "color"]
sd_def_values = ["20", "0", "MODE_SMA", "PRICE_CLOSE", "#ffff80"]

atr_params = ["Period", "Color"]
atr_param_types = ["int", "color"]
atr_def_values = ["20", "#ffff80"]

so_params = ["KPeriod", "DPeriod", "Slowing", "Mode", "STOPrice", "Color1", "Color2"]
so_param_types = ["int", "int", "int", ma_modes, so_prices, "color", "color"]
so_def_values = ["5", "3", "3", "MODE_SMA", "STO_LOWHIGH", "#ffff80", "#c0c0c0"]

sar_params = ["Step", "Maximum", "Color"]
sar_param_types =["double", "double", "color"]
sar_def_values = ["0.02", "0.2", "#ffff80"]

tema_params = ["Period", "Shift", "AppliedPrice", "Color"]
tema_param_types = ["int", "int", ind_app_price, "color"]
tema_def_values = ["20", "0", "PRICE_CLOSE", "#ffff80"]

ama_params = ["Period", "FastEMA", "SlowEMA", "Shift", "AppliedPrice", "Color"]
ama_param_types = ["int", "int", "int", "int", ind_app_price, "color"]
ama_def_values = ["9", "2", "30", "0", "PRICE_CLOSE", "#ffff80"]