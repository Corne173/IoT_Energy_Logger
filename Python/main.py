import argparse
import json
import sdm_modbus


if __name__ == "__main__":


    meter = sdm_modbus.SDM230(
        device="COM7",
        stopbits=1,
        baud=19200,
        timeout=1,
        unit=1
    )

    print(meter)
    print(meter.read_all(scaling=True))


    print("\nInput Registers:")

    for k, v in meter.read_all(sdm_modbus.registerType.INPUT).items():
        address, length, rtype, dtype, vtype, label, fmt, batch, sf = meter.registers[k]

        if type(fmt) is list or type(fmt) is dict:
            print(f"\t{label}: {fmt[str(v)]}")
        elif vtype is float:
            print(f"\t{label}: {v:.2f}{fmt}")
        else:
            print(f"\t{label}: {v}{fmt}")

    print("\nHolding Registers:")

    for k, v in meter.read_all(sdm_modbus.registerType.HOLDING).items():
        address, length, rtype, dtype, vtype, label, fmt, batch, sf = meter.registers[k]

        if type(fmt) is list:
            print(f"\t{label}: {fmt[v]}")
        elif type(fmt) is dict:
            print(f"\t{label}: {fmt[str(v)]}")
        elif vtype is float:
            print(f"\t{label}: {v:.2f}{fmt}")
        else:
            print(f"\t{label}: {v}{fmt}")